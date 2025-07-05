import Logo from "../../images/Logo_UC3M.png"

export default function Header() {
    return (
        <>
            <header className="fixed top-0 left-0 w-full h-[12.5vh] bg-main-dark-blue z-50">
                <div className="header-content">
                    <img src={Logo} alt="UC3M Organizer Logo" className="header-logo" />
                    <h1 className="header-title">Organizador</h1>
                </div>
            </header>
            <div className="h-[12.5vh]"></div>
        </>
    );
}