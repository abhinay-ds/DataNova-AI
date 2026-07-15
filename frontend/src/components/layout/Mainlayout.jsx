import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import ChatArea from "./ChatArea";
import ChatInput from "./ChatInput";
import DatasetPanel from "./DatasetPanel";

export default function MainLayout() {
  return (
    <div className="flex h-screen bg-slate-100">

      <Sidebar />

      <div className="flex flex-1 flex-col">

        <Navbar />

        <div className="flex flex-1">

          <div className="flex flex-1 flex-col">

            <ChatArea />

            <ChatInput />

          </div>

          <DatasetPanel />

        </div>

      </div>

    </div>
  );
}