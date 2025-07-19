import Header from "../components/common/Header";
import { useState } from "react";
import PendingCalendar from "../components/data_related/Pending_Calendar"

export default function Pendientes() {
  const [loading, setLoadingState] = useState(true);

  return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <PendingCalendar setLoadingState={ setLoadingState }/>
    </>
  )
}