import {Link} from "react-router-dom";
import LoginForm from "../components/forms/LoginForm";
import RegisterForm from "../components/forms/RegisterForm";
import Header from "../components/common/Header";

export default function Inicio() {
    return (
    <>
      <Header />
      <section className="login-section">
        <div className="w-1/2 flex justify-center items-center">
          <LoginForm />
        </div>
        <div className="login-separator"></div>
        <div className="w-1/2 h-full flex justify-center items-center">
          <RegisterForm />
        </div>
      </section>
    </>
  )
}