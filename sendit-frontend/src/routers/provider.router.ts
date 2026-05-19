import { createBrowserRouter, redirect } from "react-router-dom";
import SignIn from "../layouts/SignInLayout/SignIn";
import Homepage from "../layouts/Homepage/Homepage";
import Onboarding from "../layouts/SignInLayout/Onboarding";
import VerifyLayout from "../layouts/VerifyLayout/VerifyLayout";
import Offers from "../layouts/Offers/Offers";
import Send from "../layouts/Send/Send";
import Wallet from "../layouts/Wallet/Wallet";
import Profile from "../layouts/Profile/Profile";
import Chats from "../layouts/Chats/Chats";
import SpecificChat from "../layouts/Chats/SpecificChat";
import SenderDashboard from "../layouts/DashboardLayout/SenderDashboard";
import Notifications from "../layouts/Notifications/Notifications";

export const ProviderRoutePaths = {
  Root: "/", // added root
  Index: "/dashboard",
  SignIn: "/login",
  Onboarding: "/onboarding",
  Verify: "/verify",
  Homepage: "/home",
  offers: "/offers",
  send: "/send",
  wallet: "Wallet",
  profile: "/profile",
  chats: "/chats",
  specificChat: "/chats/:chatId",
  User: "/user",
  Notifications: "/notifications",
  sender: "/sender/:senderId",
  ErrorPage: "*",
};

export const ProviderRouter = createBrowserRouter([
  {
    path: ProviderRoutePaths.Root, // handle localhost/
    loader() {
      return redirect(ProviderRoutePaths.SignIn);
    },
  },
  {
    path: ProviderRoutePaths.SignIn,
    Component: SignIn,
  },
  {
    path: ProviderRoutePaths.Onboarding,
    Component: Onboarding,
  },
  {
    path: ProviderRoutePaths.Verify,
    Component: VerifyLayout,
  },
  {
    path: ProviderRoutePaths.Homepage,
    Component: Homepage,
  },
  {
    path: ProviderRoutePaths.offers,
    Component: Offers,
  },
  {
    path: ProviderRoutePaths.send,
    Component: Send,
  },
  {
    path: ProviderRoutePaths.wallet,
    Component: Wallet,
  },
  {
    path: ProviderRoutePaths.profile,
    Component: Profile,
  },
  {
    path: ProviderRoutePaths.chats,
    Component: Chats,
  },
  {
    path: ProviderRoutePaths.specificChat,
    Component: SpecificChat, // For simplicity, using the same Chats component. In a real app, this would be a ChatDetail component.
  },
  {
    path: ProviderRoutePaths.sender,
    Component: SenderDashboard,
  },
  {
    path: ProviderRoutePaths.Notifications,
    Component: Notifications,
  },
  {
    path: ProviderRoutePaths.User,
    // Component: UserDashboardLayout,
  },
]);
