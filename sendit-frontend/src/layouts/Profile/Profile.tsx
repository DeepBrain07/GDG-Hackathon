import DashboardLayout from "../DashboardLayout/DashboardLayout"
import { useNavigate } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import { profileImage } from "../../assets/images";
import { useState, useEffect } from "react";
import api from "../../api/axios";

// Interface for type safety based on your sample response
interface UserData {
    first_name: string;
    last_name: string;
    is_verified: boolean;
    avatar?: {
        file_url: string;
    };
    email: string;
}

const Profile = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState<UserData | null>(null);
    const [loading, setLoading] = useState(true);

    const options1 = {
        "Verification Center": "material-symbols-light:domain-verification-rounded",
        "Wallet ": "iconoir:wallet-solid",
        "Notifications": "solar:bell-bold",
        "Settings": "tdesign:setting-filled",
    }

    const options2 = {
        "Help Center": "material-symbols:help-rounded",
        "Log Out": "ant-design:logout-outlined"
    }

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await api.get("/users/me");
                setUser(response.data.data);
                console.log(response.data.data);
            } catch (error) {
                console.error("Failed to fetch user profile:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, []);

    return (
        <DashboardLayout>
            <div className="background !justify-start !flex !flex-col">
                {/* Background Layers */}
                <div className="gradient-layer-alt2 flex flex-col p-4 pr-8 pt-8 gap-8 !text-white !h-fit">
                    <div className='flex items-center justify-between gap-4'>
                        <div className="flex items-center jusify-start gap-4">
                            <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                            </button>
                            <h2 className="!text-xl">Profile</h2>
                        </div>
                        <p className="cursor-pointer p-2 rounded-lg bg-white !text-black !text-xs">Edit Profile</p>
                    </div>

                    <div className="flex items-center flex-col gap-2">
                        <div className="rounded-xl border-2 border-primary w-fit h-fit overflow-hidden">
                            <img 
                                src={user?.avatar?.file_url || profileImage} 
                                alt="Profile" 
                                className="size-16 object-cover rounded-xl"
                            />
                        </div>
                        <div className="flex items-center gap-1">
                            <h2 className="!font-bold !text-xl">
                                {loading ? "Loading..." : `${user?.first_name} ${user?.last_name}`}
                            </h2>
                            {user?.is_verified && (
                                <Icon icon="fluent-mdl2:verified-brand-solid" width={16} className="text-primary"/>
                            )}
                        </div>
                    </div>

                    {/* stats */}
                    <div className="p-2 px-3 rounded-xl bg-gray-100 w-full flex items-center justify-between gap-4">
                        <div className="flex flex-col gap-1 items-center justify-center">
                            <h2 className="!text-xl !text-black !font-black">12</h2>
                            <p className="!text-sm !text-bodyText/80">Deliveries</p>
                        </div>
                        <div className="flex flex-col gap-1 items-center justify-center">
                            <h2 className="!text-xl !text-black !font-black">4.9</h2>
                            <p className="!text-sm !text-bodyText/80">Rating</p>
                        </div>
                        <div className="flex flex-col gap-1 items-center justify-center">
                            <h2 className="!text-xl !text-black !font-black">98%</h2>
                            <p className="!text-sm !text-bodyText/80">Response</p>
                        </div>
                    </div>
                </div>

                <div className="mt-[320px] p-4 w-full pr-8">
                    {/* Options 1 */}
                    <div className="bg-gray-100 rounded-xl border-1 border-gray-200 flex flex-col items-start w-full">
                        {Object.entries(options1).map(([option, icon], index) => (
                            <div 
                                key={option} 
                                onClick={() => navigate('/notifications')}
                                className={`cursor-pointer hover:bg-gray-200 ${index > 0 && 'border-t-1 border-gray-200'} flex items-center gap-4 p-4 rounded-lg transition-colors w-full`}
                            >
                                <div onClick={() => navigate('/notifications')} className="flex gap-2 justify-center items-center">
                                    <div className="p-2 bg-white rounded-[50%]">
                                        <Icon icon={icon} width={24} className="text-black"/>
                                    </div>
                                    <p className="!text-sm !text-bodyText">{option}</p>
                                </div>
                                <Icon icon="iconamoon:arrow-right-2-duotone" width={20} className="text-bodyText/80 ml-auto"/>
                            </div>
                        ))}
                    </div>

                    {/* Options 2 */}
                    <div className="mt-6 bg-gray-100 rounded-xl border-1 border-gray-200 flex flex-col items-start w-full">
                        {Object.entries(options2).map(([option, icon], index) => (
                            <div key={option} className={`cursor-pointer hover:bg-gray-200 ${index > 0 && 'border-t-1 border-gray-200'} flex items-center gap-4 p-4 rounded-lg transition-colors w-full`}>
                                <div className="flex gap-2 justify-center items-center">
                                    <div className="p-2 bg-white rounded-[50%]">
                                        <Icon icon={icon} width={24} className={`${option === 'Log Out' ? 'text-red-500' : 'text-black'}`}/>
                                    </div>
                                    <p className="!text-sm !text-bodyText">{option}</p>
                                </div>
                                <Icon icon="iconamoon:arrow-right-2-duotone" width={20} className="text-bodyText/80 ml-auto"/>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}

export default Profile;