import axios from "axios";

const api = axios.create({
    // baseURL: "http://172.17.200.48:8021/api/nurse-education-portal",
    baseURL: "http://localhost:8021/api/cohr",
    withCredentials: true,
});

export { api };