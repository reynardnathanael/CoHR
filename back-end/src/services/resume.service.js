const bcrypt = require('bcrypt');
const axios = require("axios");
const crypto = require('crypto');
const { PDFParse } = require('pdf-parse');

class ResumeService {
    async read(data) {
        if (!data) {
            return {
                status: false,
                message: 'Data required',
                code: 400,
            }
        }
        else {
            const buffer = await data.toBuffer();
            const parser = new PDFParse({ data: buffer });
            const result = await parser.getText();
            return {
                status: true,
                message: 'PDF Extracted Successfully',
                data: result.text,
                code: 200,
            }
        }
    }
}

module.exports = new ResumeService();