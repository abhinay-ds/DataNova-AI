import { Database, Upload, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useDataset } from "../context/DatasetContext";
export default function Datasets() {
  const navigate = useNavigate();
  const { dataset } = useDataset();
  const filename = dataset?.filename || dataset?.file_name;
  return <div className="simple-page"><div className="simple-top"><div className="brand-inline"><span className="brand-mark"><Sparkles size={17}/></span><strong>DataNova AI</strong></div><button className="ghost-button" onClick={()=>navigate('/workspace')}>Back to workspace</button></div><div className="simple-content wide"><div className="page-icon"><Database/></div><span className="section-kicker">Datasets</span><h1>Your data</h1><p>Datasets are available to the active workspace session.</p>{filename ? <div className="dataset-list-card"><div><strong>{filename}</strong><span>Currently loaded</span></div><button className="primary-button" onClick={()=>navigate('/workspace')}>Analyze</button></div> : <div className="empty-card"><Upload size={22}/><strong>No dataset loaded</strong><span>Upload CSV, Excel or JSON from the AI workspace.</span><button className="primary-button" onClick={()=>navigate('/workspace')}>Upload dataset</button></div>}</div></div>;
}
