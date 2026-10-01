import { CheckSquare, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
export default function Tasks() {
  const navigate = useNavigate();
  return <div className="simple-page"><div className="simple-top"><div className="brand-inline"><span className="brand-mark"><Sparkles size={17}/></span><strong>DataNova AI</strong></div><button className="ghost-button" onClick={()=>navigate('/workspace')}>Back to workspace</button></div><div className="simple-content"><div className="page-icon"><CheckSquare/></div><span className="section-kicker">Tasks</span><h1>AI task history</h1><p>Completed and running analysis tasks will appear here.</p><button className="primary-button" onClick={()=>navigate('/workspace')}>Open AI workspace</button></div></div>;
}
