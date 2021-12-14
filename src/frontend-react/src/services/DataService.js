import { BASE_API_URL } from "./Common";

const axios = require('axios');

const DataService = {
    Init: function () {
        // Any application initialization logic comes here
    },
    GetLeaderboard: async function () {
        return await axios.get(BASE_API_URL + "/leaderboard");
    },
    GetCurrentmodel: async function () {
        return await axios.get(BASE_API_URL + "/best_model");
    },
    Predict: async function (formData) {
        return await axios.post(BASE_API_URL + "/v1/predict", formData);
    },

    PlotsGetData: async function () {
        return await axios.get(BASE_API_URL + "/plots/get_data");
    },
    GetCurrentTopOfBookData: async function () {
        return await axios.get(BASE_API_URL + "/v1/get_current_top_of_book");
    },


}

export default DataService;