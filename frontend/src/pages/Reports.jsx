import { FileBarChart2, Plus, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
export default function Reports() {
  const navigate = useNavigate();
  return <div className="simple-page"><div className="simple-top"><div className="brand-inline"><span className="brand-mark"><Sparkles size={17}/></span><strong>DataNova AI</strong></div><button className="ghost-button" onClick={()=>navigate('/workspace')}>Back to workspace</button></div><div className="simple-content"><div className="page-icon"><FileBarChart2/></div><span className="section-kicker">Reports</span><h1>Analysis reports</h1><p>Your generated reports will appear here.</p><button className="primary-button" onClick={()=>navigate('/workspace')}><Plus size={17}/> Create a report</button></div></div>;
}
