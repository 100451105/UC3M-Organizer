export default function Loading({ loadingInProgress }) {
    return (
        <>
            {loadingInProgress && (
                <div className="fixed inset-0 z-50 bg-black bg-opacity-20 flex items-center justify-center">
                    <div className="w-[20vh] h-[20vh] border-[2.5vh] border-main-dark-blue border-t-transparent rounded-full animate-spin"></div>
                </div>
            )}
        </>
        
    );
}