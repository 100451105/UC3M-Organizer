import axios from "axios";

export async function ActivityCache() {
    const now = new Date();

    const activity_info = JSON.parse(localStorage.getItem("activity_info"));
    let refreshCache = false;
    if (!activity_info) {
        refreshCache = true;
    } else {
        const minutesSinceCache = (now - new Date(activity_info.updatedAt)) / 1000 / 60;
        if (minutesSinceCache > 30 || activity_info.activities.length === 0) {
            refreshCache = true;
        }
    }
    if (refreshCache) {
        try {
            const today = new Date();
            const year = today.getUTCFullYear();
            const month = String(today.getUTCMonth() + 1).padStart(2, '0');
            const day = String(today.getUTCDate()).padStart(2, '0');
            const dateString = `${year}-${month}-${day}`;
            console.log(dateString)
            const response = await axios.get("http://localhost:8002/activities/info/",{
                    withCredentials: true,
                    params: {
                        actualDate: dateString
                    }
                });
            if (response.status === 200) {
                const activities = response.data.activities;
                const activityCache = {
                    activities: activities,
                    updatedAt: new Date().toISOString(),
                };
                localStorage.removeItem("activity_info");
                localStorage.setItem("activity_info", JSON.stringify(activityCache));
                return activities;
            }
        } catch (error) {
            console.error("Error al obtener las actividades:", error);
            return [];
        }
    } else {
        return activity_info.activities;
    }
}

export async function UserCache(Id) {
    const now = new Date();

    const user_info = JSON.parse(localStorage.getItem("user_info"));
    let refreshCache = false;
    if (!user_info) {
        refreshCache = true;
    } else {
        const minutesSinceCache = (now - new Date(user_info.updatedAt)) / 1000 / 60;
        if (minutesSinceCache > 30) {
            refreshCache = true;
        }
    }
    if (!user_info.Id || (user_info.Id !== Id && Id !== false)){
        refreshCache = true
    }
    if (Id === false) {
        refreshCache = true
    }
    if (!user_info.relatedSubjectsList) {
        refreshCache = true
    }
    {/* Si necesita refrescar la caché, obtiene la información de nuevo del usuario */}
    if (refreshCache) {
        try {
            let userId = 0;
            if (!user_info || (user_info.Id !== Id && Id)) {
                userId = Id;
            } else {
                userId = user_info.Id;
            }

            const response = await axios.get("http://localhost:8002/user/info/",{
                    withCredentials: true,
                    params: {
                        userId: userId
                    }
                });
            if (response.status === 200) {
                const userInfo = response.data.userInformation;
                const subjectList = response.data.subjectsOfUser;
                const userCache = {
                    ...userInfo,
                    relatedSubjectsList: subjectList,
                    updatedAt: new Date().toISOString(),
                };
                localStorage.removeItem("user_info");
                localStorage.setItem("user_info", JSON.stringify(userCache));
                return;
            }
        } catch (error) {
            console.error("Error al obtener la información de usuario:", error);
            return;
        }
    } else {
        return;
    }
}