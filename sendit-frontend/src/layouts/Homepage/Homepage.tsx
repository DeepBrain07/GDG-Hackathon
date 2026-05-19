import DashboardLayout from "../DashboardLayout/DashboardLayout"
import { profileImage } from "../../assets/images";
import { Icon } from "@iconify/react/dist/iconify.js";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";

const Homepage = () => {
    const navigate = useNavigate();
    const [selected, setSelected] = useState("");
    const [offers, setOffers] = useState<any[]>([]); // State for offers
    const [userData, setUserData] = useState<any>(() => {
        try {
            const user = localStorage.getItem('user');
            return JSON.parse(user || '{}');
        } catch (e) {
            return {};
        }
    });

    const places = ["Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan", "Enugu"];

    useEffect(() => {
    const fetchUserData = async () => {
        try {
            const response = await api.get("/users/me/");
            const freshData = response.data.data;

            // 1. Get the existing data first
            const existingUser = JSON.parse(localStorage.getItem('user') || '{}');
            console.log("Existing User Data from localStorage:", existingUser);
            console.log("Fresh User Data from API:", freshData);

            // 2. Merge them: freshData will update existing keys, 
            // but won't delete keys that are only in existingUser
            const mergedData = { ...existingUser, ...freshData };

            setUserData(mergedData);
            localStorage.setItem('user', JSON.stringify(mergedData));
        } catch (error) {
            console.error("Failed to refresh user data:", error);
        }
    };

    const fetchOffers = async () => {
        try {
            const response = await api.get("/offers/");
            setOffers(response.data.offers || response.data.results || []);
        } catch (error) {
            console.error("Failed to fetch offers:", error);
        }
    };

    fetchUserData();
    fetchOffers();
}, []);

    console.log("Offers:", offers);
    const avatarUrl = userData?.avatar?.file_url || userData?.profile?.avatar?.file || profileImage;
    const firstName = userData?.first_name || "User";

    return (
        <DashboardLayout>
            <div className="background !justify-start !flex !flex-col">
                {/* Background Layers */}
                <div className="gradient-layer-alt2 flex flex-col p-4 pr-8 py-14 gap-12 !text-white !h-fit">
                    <div className="flex justify-between w-full ">
                        <div className="flex  gap-2">
                            <div className="rounded-[50%] shrink-0 w-fit h-fit">
                                <img src={avatarUrl} alt="Profile" className="size-10 rounded-[50%] object-cover"/>
                            </div>
                            <p>Good morning,<br/><span className="!font-bold"> {firstName} </span></p>
                        </div>
                        {/* notification */}
                        <div className="w-fit shrink-0 h-fit p-2 rounded-[50%]  bg-white">
                            <Icon icon="tabler:bell" width={20} className="text-black shrink-0"/>
                        </div>
                    </div>
                    {/* Location */}
                    <div className="flex flex-col gap-4 !z-10">
                        <h2 className="!font-extralight">Where's your package going?</h2>
                        <div className="w-full p-4 rounded-full flex items-center gap-2 bg-white !text-black/80">
                            <Icon icon="tdesign:search" width={20} className="shrink-0"/>
                            <input 
                                type="text" 
                                placeholder="Search destination city..." 
                                className="flex-1 w-full  bg-transparent outline-none" 
                                />
                        </div>
                        <div className="flex gap-4 overflow-x-scroll !text-white scrollbar-hide">
                            {places.map((place) => (
                                <div key={place} className="cursor-pointer shrink-0 p-2 py-1 rounded-full bg-[#001F72]">
                                    <p>{place}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="z-10 px-4  w-full flex flex-col gap-8 mt-[420px]">
                    {/* QuickActions */}
                    <div className="flex flex-col w-full items-start gap-4 !text-black">
                        <h2 className="!font-extralight !text-xl">Quick Actions</h2>
                        <div className="flex w-full gap-4 overflow-x-scroll p-2 scrollbar-hide">
                            <div onClick={() => {setSelected("Send Package"); navigate("/send")}}>
                                <QuickActionsCard selected={selected === "Send Package"} title="Send Package" icon="mingcute:package-2-fill" details="Post what you need delivered."/>
                            </div>
                            <div onClick={() => {setSelected("Browse Offers"); navigate("/offers")}}>
                                <QuickActionsCard selected={selected === "Browse Offers"} title="Browse Offers" icon="wpf:search" details="See available package offers. "/>
                            </div>
                            <div onClick={() => {setSelected("Fund wallet"); navigate("/wallet")}}>
                                <QuickActionsCard selected={selected === "Fund wallet"} title="Fund wallet" icon="ion:wallet" details="Add money for quick payments."/>
                            </div>
                        </div>
                    </div>

                    {/* Recent Activities - Now showing live Offers */}
                    <div className="mt-12 flex flex-col w-full items-start gap-4 !text-black pb-12">
                        <div className="flex items-center justify-between w-full pr-4">
                            <h2 className="!font-extralight !text-xl">Recent Offers</h2>
                            <p className="text-primary hover:underline cursor-pointer" onClick={() => navigate("/offers")}>See all</p>
                        </div>
                        <div className="flex flex-col w-full gap-4 p-2">
                            {offers.slice(0, 5).map((offer: any) => (
                                <RecentActivitiesCard 
                                    key={offer.id}
                                    carrier={offer.status === 'delivered'} 
                                    from={offer.pickup_location?.city}
                                    to={offer.delivery_location?.city}
                                    amount={offer.total_price} 
                                    name={offer.sender?.first_name || "Unknown"}
                                />
                            ))}
                            {offers.length === 0 && <p className="text-gray-400 text-sm">No recent activities found.</p>}
                        </div>
                    </div>
                </div>
            </div>

        </DashboardLayout>
    )
}

const QuickActionsCard = ({ title, icon, details, selected }: { title: string, icon: string, details: string, selected: boolean }) => {
    return (
        <div className={`${selected ? 'ring-2 ring-primary' : ''} border-1 border-gray-100 rounded-xl p-4 hover:ring-2 hover:ring-primary shrink-0 w-[150px] shadow-xs cursor-pointer flex flex-col items-start bg-gray-50 text-black/80'`}>
            <Icon icon={icon} width={26} className='text-primary'/>
            <p className="!font-black mt-1">{title}</p>
            <p className="text-left !text-[12px]  !text-black/60">{details}</p>
        </div>
    )
}

const RecentActivitiesCard = ({ from, to, carrier, amount, name }: { from: string, to: string, carrier: boolean, amount: string, name: string }) => {
    return (
        <div className="border-1 border-gray-100 rounded-xl p-4 shrink-0 w-full shadow-xs cursor-pointer flex justify-between gap-8 bg-gray-50 text-black/80">
            <div className="flex gap-2 items-start justify-start">
                {carrier ? <div className="p-1 rounded-[50%] text-primary bg-white"><Icon icon="mage:package-box-fill" width={26} /></div> : <div className="p-1 rounded-[50%] text-primary bg-white"><Icon icon="material-symbols:luggage-rounded" width={26} /></div>}
                <div className="flex flex-col">
                    <div className="flex items-center gap-1">
                        <p className="!font-black !text-sm ">{from}</p>
                        <Icon icon="tabler:arrow-right" width={20} className='inline text-bodyText/80'/>
                        <p className="!font-black !text-sm">{to}</p>
                    </div>
                    <p className="text-left !text-[12px]  !text-black/60">{carrier ? 'Carrier:' : 'Sender:'}: <span className="!text-black">{name}</span></p>
                    <div className="flex gap-1">
                        <p className="text-left !text-[12px]  !text-black/60">Delivered recently</p>
                        <Icon icon="lets-icons:check-fill" width={16} className='text-green-500'/>
                    </div>
                    <p className="w-fit !font-black p-1 px-4 mt-2 hover:border-1 hover:border-primary  rounded-full bg-gray-200">View</p>
                </div>
            </div>
            <p className="!font-black">₦{amount}</p>
        </div>
    )
}

export default Homepage;