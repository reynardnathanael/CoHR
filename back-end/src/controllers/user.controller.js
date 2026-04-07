const UserService = require("../services/user.service");
const replyHandling = require("../helpers/reply-handling");

class UserController {
    async all(request, reply) {
        const data = await UserService.all();

        if (data === false) {
            replyHandling.sendReply(reply, 404, false, "No data found", null);
        }
        else {
            replyHandling.sendReply(reply, 200, true, "Get all user data successfully", data);
        }
    }

    async register(request, reply) {
        // const user = JSON.parse(request.cookies['user']);
        const data = await UserService.register(request.body);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }

    async login(request, reply) {
        const data = await UserService.login(request.body);

        if(data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            let {id, username, password} = data.data;
            const token = request.server.jwt.sign({id, username, password});
            reply.code(200).header(`Content-Type`, `application/json; charset=utf-8`)
            .setCookie('jwtToken', token, {
                // secure: true,
                path: '/',
                httpOnly: true,
                sameSite: 'strict'
            })
            .setCookie('user', JSON.stringify(data.data), {
                // secure: true,
                path: '/',
                httpOnly: true,
                sameSite: 'strict'
            })
            .send({
                status: true,
                message: data.message,
                data: data.data,
                token: token,
            });
        }
    }

    async logout(request, reply) {
        reply.code(200).header(`Content-Type`, `application/json; charset=utf-8`)
        .clearCookie('jwtToken')
        .clearCookie('user')
        .send({
            status: true,
            message: 'Logged out successfully!',
        });
    }

    async resetPassword(request, reply) {
        const user = JSON.parse(request.cookies['user']);
        const data = await UserService.resetPassword(request.body, user.id);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }

    async resetPasswordDefault(request, reply) {
        const user = JSON.parse(request.cookies['user']);
        const data = await UserService.resetPasswordDefault(request.body, user.id);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }

    async deleteUser(request, reply) {
        const user = JSON.parse(request.cookies['user']);
        const data = await UserService.deleteUser(request.body.id, user.id);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }

    async createPostUser(request, reply) {
        const user = JSON.parse(request.cookies['user']);
        const data = await UserService.createPostUser(request.body.id, user.id);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }

    async viewPostUsers(request, reply) {
        const data = await UserService.viewPostUsers(request.body.id);

        if (data.status === false) {
            replyHandling.sendReply(reply, data.code, data.status, data.message, null);
        }
        else {
            replyHandling.sendReply(reply, 200, data.status, data.message, data.data);
        }
    }
}

module.exports = new UserController();