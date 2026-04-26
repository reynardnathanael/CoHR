const db = require("../helpers/database");
const bcrypt = require("bcrypt");
const generate = require("../helpers/generate");

class ResumeRepository {
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
}

module.exports = new ResumeRepository();