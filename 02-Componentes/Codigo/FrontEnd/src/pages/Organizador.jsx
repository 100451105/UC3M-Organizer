import Header from "../components/common/Header";
import CustomCalendar from "../components/data_related/Calendar"

export default function Organizador() {
    return (
    <>
      <Header showIndex={true} loadingInProgress={false}/>
      <CustomCalendar />
    </>
  )
}