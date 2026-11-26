
import axios from "axios";

export const translateDocument = async (
  file: File,
  beamSize: number = 4
): Promise<Blob> => {

  const formData = new FormData();

  formData.append("file", file);
  formData.append("beam_size", String(beamSize));

  try {

    const response = await axios.post(
      "/api/documents/translate",
      formData,
      {
        responseType: "blob",
        timeout: 600000
      }
    );

    return response.data;

  } catch (error) {

    if (axios.isAxiosError(error)) {

      const data = error.response?.data;

      if (data instanceof Blob) {

        const text = await data.text();

        let message = text;

        try {
          const json = JSON.parse(text);

          if (typeof json.detail === "string") {
            message = json.detail;
          }
        } catch {
          // Keep the original error message.
        }

        throw new Error(message || "Document translation failed.");
      }

      throw new Error(
        error.message || "Cannot connect to Backend."
      );
    }

    throw error;
  }
};
