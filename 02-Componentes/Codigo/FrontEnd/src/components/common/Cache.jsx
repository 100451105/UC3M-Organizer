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