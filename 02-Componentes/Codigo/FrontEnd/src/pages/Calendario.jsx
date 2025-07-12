import Header from "../components/common/Header";
import GanttDiagram from "../components/data_related/Gantt";

export default function Calendario() {
    return (
    <>
      <Header showIndex={true} loadingInProgress={false}/>
      <GanttDiagram />
    </>
  )
}