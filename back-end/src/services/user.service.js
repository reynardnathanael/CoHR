const bcrypt = require('bcrypt');
const UserRepository = require("../repository/user.repository");
const axios = require("axios");
const crypto = require('crypto');

class UserService {
    async all() {
        const user = await UserRepository.all();
        return user.length === 0 ? false : user;
    }

    async register(data) {
        if (!data.name || !data.username || !data.password || data.name === '' || data.username === '' || data.password === '') {
            return {
                status: false,
                message: 'Data required',
                code: 400,
            }
        }
        else {
            const checkUsername = await UserRepository.checkUsername(data.username);
            if (checkUsername) {
                return {
                    status: false,
                    message: 'Username already exists!',
                    code: 401,
                }
            }
            else {
                const newUser = await UserRepository.register(data.username, data.password, data.name);
                return {
                    status: true,
                    message: 'User register successful',
                    data: newUser[0],
                }
            }
        }
    }
}

module.exports = new UserService();