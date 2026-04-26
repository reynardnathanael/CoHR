const ResumeController = require("../controllers/resume.controller");

module.exports = async (fastify) => {
    fastify.post(`/upload-resume`, ResumeController.read)
}