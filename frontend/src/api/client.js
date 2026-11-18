import axios from "axios";

const configuredApiUrl = import.meta.env.VITE_API_URL;

const apiClient = axios.create({
    baseURL: configuredApiUrl
        ? configuredApiUrl.replace(/\/+$/, "")
        : "http://127.0.0.1:8000",

    timeout: 120000,

    headers: {
        Accept: "application/json",
    },
});

// Attach authentication token to requests.
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(
            "researchrag_token"
        );

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Normalize API errors.
apiClient.interceptors.response.use(
    (response) => response,

    (error) => {
        if (error.response) {
            console.error(
                "API Error:",
                error.response.status,
                error.response.data
            );
        } else if (error.request) {
            console.error(
                "API unavailable:",
                error.message
            );
        }

        return Promise.reject(error);
    }
);

export default apiClient;