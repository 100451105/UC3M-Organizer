import {Link} from "react-router-dom";
import {useState} from "react";
import LoginForm from "../components/forms/LoginForm";
import RegisterForm from "../components/forms/RegisterForm";
import Header from "../components/common/Header";


export default function Inicio() {
  const [loading, setLoadingState] = useState(false);

  return (
    <>
      <Header showIndex={false} loadingInProgress={loading} />
      <section className="login-section">
        <div className="w-1/2 flex justify-center items-center">
          <LoginForm setLoadingState={setLoadingState}/>
        </div>
        <div className="login-separator"></div>
        <div className="w-1/2 h-full flex justify-center items-center">
          <RegisterForm setLoadingState={setLoadingState}/>
        </div>
      </section>
    </>
  );
}