import { createContext, useContext, useState } from "react";

const DatasetContext = createContext();

export function DatasetProvider({ children }) {
  const [dataset, setDataset] = useState(null);

  return (
    <DatasetContext.Provider value={{ dataset, setDataset }}>
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  return useContext(DatasetContext);
}