import Header from "../components/common/Header";
import { useState } from "react";
import CustomCalendar from "../components/data_related/Calendar";

export default function Organizador() {
  const [loading, setLoadingState] = useState(true);
  return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <CustomCalendar setLoadingState={ setLoadingState }/>
    </>
  )
}