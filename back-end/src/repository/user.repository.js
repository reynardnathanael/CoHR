const db = require("../helpers/database");
const bcrypt = require("bcrypt");
const generate = require("../helpers/generate");

class UserRepository {
    async all() {
        return await db.select('*').from('users').orderBy('created_at', 'desc');
    }

    async register(username, password, name) {
        return await db.insert({
            username: username,
            password: await bcrypt.hash(password, 10),
            name: name,
            created_at: generate.getCurrentTimestamp(),
        })
        .returning('*')
        .into('users');
    }

    async checkUsername(username) {
        return await db.first('*').from('users').where('username', username);
    }

    // async getUser(id) {
    //     return await db.first('*').from('users').where('id', id).where('is_deleted', 0);
    // }

    // async resetPassword(data) {
    //     return await db('users').update({
    //         password: await bcrypt.hash(data.new_password, 10),
    //         updated_at: generate.getCurrentTimestamp(),
    //     })
    //     .where('id', data.id)
    //     .returning('*');
    // }

    // async deleteUser(id) {
    //     return await db('users').update({
    //         is_deleted: 1,
    //         updated_at: generate.getCurrentTimestamp(),
    //     })
    //     .where('id', id)
    //     .returning('*');
    // }

    // async checkPostUser(post_id, user_id) {
    //     return await db.first('*').from('post_users').where('post_id', post_id).where('user_id', user_id);
    // }

    // async createPostUser(post_id, user_id) {
    //     return await db.insert({
    //         post_id: post_id,
    //         user_id: user_id,
    //         timestamp: generate.getCurrentTimestamp(),
    //     })
    //     .returning('*')
    //     .into('post_users');
    // }

    // async viewPostUsers(post_id) {
    //     return await db.select('users.username', 'users.name', 'post_users.timestamp').from('users').join('post_users', 'users.id', 'post_users.user_id').where('post_users.post_id', post_id);
    // }
}

module.exports = new UserRepository();