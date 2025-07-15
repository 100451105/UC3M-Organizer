import Header from "../components/common/Header";
import { useState } from "react";
import GanttDiagram from "../components/data_related/Gantt";

export default function Calendario() {
  const [loading, setLoadingState] = useState(true);

  return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <GanttDiagram setLoadingState={ setLoadingState }/>
    </>
  )
}