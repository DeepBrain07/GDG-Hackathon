import { useEffect, useState } from 'react';
import '../SignInLayout/style.css'
import { PhoneInput } from './PhoneInput';
// import PhoneVerification from './PhoneVerification';
import { IdentityVerification } from './IdentityVerification';
import { FaceVerification } from './FaceVerification';
import { Congratulations } from './congratulations';
import api from '../../api/axios';

const VerifyLayout = () => {
  const [step, setStep] = useState<number>(1);
  const [phone, setPhone] = useState<string>("");
  const [identificationData, setIdentificationData] = useState<any>(null);
  const [faceData, setFaceData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const dataURLtoFile = (dataurl: string, filename: string) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)![1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const typeMapper: Record<string, string> = {
    "NIN Slip": "nin",
    "International Passport": "passport",
    "Driver License": "driver_license",
    "Voter Card": "voter_card"
  };

  useEffect(() => {
    const triggerVerificationFlow = async () => {
      if (!isLoading || !faceData) return;

      try {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        console.log(storedUser)
        const userId = storedUser.data.id;

        if (!userId) {
          console.error("User session missing");
          setIsLoading(false);
          return;
        }

        /**
         * 1. Update Profile (PATCH)
         */
        const profileFormData = new FormData();
        profileFormData.append('phone_number', phone);
        profileFormData.append('type', 'carrier');
        profileFormData.append('is_new_user', "false"); 
        
        const base64Selfie = faceData.image || faceData; 
        if (base64Selfie && typeof base64Selfie === 'string') {
          const imageFile = dataURLtoFile(base64Selfie, `avatar_${userId}.jpg`);
          profileFormData.append('image', imageFile);
        }

        console.log("Submitting Profile Update...");
        const profileResponse = await api.patch(`/users/${userId}/profiles/`, profileFormData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        /**
         * 2. Create Verification Record (POST)
         */
        if (identificationData) {
          console.log("Submitting Verification Record...");
          const verifyFormData = new FormData();

          // backend field: verification_type
          const rawType = identificationData.documentType || identificationData.type;
          const backendType = typeMapper[rawType] || (rawType ? rawType.toLowerCase() : "nin");
          verifyFormData.append('verification_type', backendType); 

          // backend field: id_number
          const idNum = identificationData.idNumber || identificationData.id_number || identificationData.number;
          verifyFormData.append('id_number', idNum);

          // Append Selfie File (for GenericRelation processing)
          if (base64Selfie && typeof base64Selfie === 'string') {
            const selfieFile = dataURLtoFile(base64Selfie, `selfie_${userId}.jpg`);
            verifyFormData.append('selfie', selfieFile);
          }

          // Append Document File (for GenericRelation processing)
          const docBase64 = identificationData.image || identificationData.document;
          if (docBase64 && typeof docBase64 === 'string') {
            const docFile = dataURLtoFile(docBase64, `document_${userId}.jpg`);
            verifyFormData.append('document', docFile);
          }

          await api.patch(`/users/${userId}/profiles/`, verifyFormData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        }

        /**
         * 3. Sync Local Storage
         */
        const updatedUser = {
            ...storedUser,
            profile: {
                ...profileResponse.data,
                is_new_user: false 
            }
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setStep(5);

      } catch (error: any) {
        const errorData = error.response?.data;
        console.error("❌ API Error:", errorData || error.message);
        const errorMessage = typeof errorData === 'object' 
          ? Object.values(errorData).flat()[0] 
          : "Could not complete verification.";
        alert(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    triggerVerificationFlow();
  }, [isLoading, faceData]);

  return (
    <div className="background !justify-start">
      <div className="gradient-layer-alt" />
      <div className={`px-8 w-full flex items-center ${step > 1 ? 'justify-between' : 'justify-end'} my-12`}>
        {step > 1 && step < 5 && (
          <button onClick={() => setStep(prev => prev - 1)} className="p-2 -ml-2 bg-white rounded-[50%]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
        {step < 5 && (
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className={`h-1 w-8 rounded-full ${i <= step ? 'bg-blue-700' : 'bg-blue-100'}`} />
            ))}
          </div>
        )}
      </div>
      <div className='w-full'>
        {step === 1 && <PhoneInput setStep={setStep} setPhone={setPhone} />}
        {/* {step === 2 && <PhoneVerification phone={phone} setStep={setStep}/>} */}
        {step === 3 && <IdentityVerification setIdentificationData={setIdentificationData} setStep={setStep} />}
        {step === 4 && (
          <FaceVerification 
            loading={isLoading} 
            setFaceData={setFaceData} 
            setIsLoading={setIsLoading} 
            setStep={setStep}
          />
        )}
        {step === 5 && <Congratulations />}
      </div>
    </div>
  );
};

export default VerifyLayout;