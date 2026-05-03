const ResumeService = require("../services/resume.service");
const replyHandling = require("../helpers/reply-handling");

class ResumeController {
    async read(request, reply) {
        // const pdf = await request.file(); 
        const pdf = request.body?.file;
        console.log(pdf)
        if (!pdf) {
            replyHandling.sendReply(reply, 404, false, "No file uploaded", null);
        }
        else {
            const data = await ResumeService.read(pdf);
            replyHandling.sendReply(reply, data.code, data.status, data.message, data.data);
            console.log(data.data)
        }
    }

    async all(request, reply) {
        const data = await ResumeService.all();

        if (data === false) {
            replyHandling.sendReply(reply, 404, false, "No data found", null);
        }
        else {
            replyHandling.sendReply(reply, 200, true, "Get all user data successfully", data);
        }
    }
}

module.exports = new ResumeController();