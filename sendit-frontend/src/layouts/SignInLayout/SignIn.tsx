import { useState } from 'react';
import { logo, bgLogo } from '../../assets/images';
import './style.css';
import { Button } from '../../components/Button';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function SignIn() {
  const navigate = useNavigate();
  const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;
  const [isLoading, setIsLoading] = useState(false);

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        console.log('Google Login Success, token response:', tokenResponse.access_token);
        const cleanToken = tokenResponse.access_token.trim();
        
        // 1. Send the token to the backend
        const response = await axios.post(
          `${BACKEND_URL}/users/google/login/`,
          { "id_token": cleanToken },
          { withCredentials: true } 
        );

        // 2. The backend returns something like: 
        // { status: 'Success', data: { id: '...', profile: { is_new_user: true }, ... } }
      
        const userData = response.data;
        console.log("User Data from Backend:", userData);
        const isNewUser = userData.data.profile?.is_new_user;
        

        // 3. Save user data to localStorage
        // This includes the profile object so ProtectedRoutes can check it
        localStorage.setItem('user', JSON.stringify(userData));

        /**
         * 4. Routing Logic
         * If they are a new user (haven't completed VerifyLayout), send to verify.
         * Otherwise, send to the main app dashboard.
         */
        if (isNewUser === true) {
          navigate('/onboarding');
        } else {
          navigate('/home'); // or wherever your main landing page is
        }
        
      } catch (error: any) {
        console.error('Login Error details:', error.response?.data);
        alert('Authentication failed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google Login Failed:', error);
      setIsLoading(false);
    }
  });

  const handleGoogleClick = () => {
    setIsLoading(true);
    login();
  };

  return (
    <div className="background">
      {/* Background Layers */}
      <div className="gradient-layer" />
      <div 
        className="image-layer" 
        style={{ backgroundImage: `url(${bgLogo})` }} 
      />

      {/* 1. Header Logo */}
      <div className="pt-16 w-full flex justify-center">
        <img src={logo} alt="Sendit" className="h-8" />
      </div>

      {/* 2. Middle Hero Text */}
      <div className=" px-8 text-center my-24">
        <h1 className="text-white text-4xl font-extrabold leading-tight">
          Send it with <br /> someone going <br /> your way.
        </h1>
        <p className="text-white mt-8 leading-relaxed">
          By continuing, you agree to the <span className="font-bold">Sendit Terms of Service</span>, and 
          acknowledge you've read our <span className="font-bold">Privacy Policy</span>
        </p>
      </div>

      {/* 3. Auth Buttons */}
      <div className="w-full flex flex-col items-center gap-4 px-6 pb-12">
        <Button 
          onClick={handleGoogleClick} 
          className='bg-white !text-black w-full' 
          title={isLoading ? 'Connecting...' : 'Continue with Google'} 
          icon='logos:google-icon' // Updated to a standard google icon name
          disabled={isLoading}
        />

        <Button 
          onClick={() => {/* Implement Apple Login logic later */}} 
          className='bg-white/50 !text-black w-full' 
          title='Continue with Apple' 
          icon='bitbtn:apple-dark'
          disabled={isLoading}
        />

        {/* <p className="text-sm mt-4 text-white/80">
          Already have an account? <span className="font-bold cursor-pointer text-white underline" onClick={() => navigate('/onboarding')}>Log In</span>
        </p> */}
      </div>
    </div>
  );
}

export default SignIn;