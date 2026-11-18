import apiClient from "./client";

export async function uploadDocument(file, onProgress) {
    const formData = new FormData();

    formData.append("file", file);

    const response = await apiClient.post(
        "/index/pdf",
        formData,
        {
            onUploadProgress: (event) => {
                if (event.total && onProgress) {
                    const percentage = Math.round(
                        (event.loaded * 100) / event.total
                    );

                    onProgress(percentage);
                }
            },
        }
    );

    return response.data;
}