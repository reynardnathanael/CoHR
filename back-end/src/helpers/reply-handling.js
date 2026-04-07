const sendReply = (reply, code, status, msg, data) => {
    reply.code(code).header(`Content-Type`, `application/json; charset=utf-8`)
    .send({
        status: status,
        message: msg,
        data: data,
    });
}

module.exports = { sendReply };