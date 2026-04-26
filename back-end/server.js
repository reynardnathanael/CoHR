require("dotenv").config();
const fastify = require("fastify")({ logger: true });
const fastifyCors = require("@fastify/cors");

const ip = "0.0.0.0";
// const ip = "192.168.1.155";
// const ip = "192.168.4.156";

const createServer = async (options) => {
    try {
        fastify.register(fastifyCors, {
            credentials: true,
            origin: true,
        });

        fastify.register(require('@fastify/jwt'), {
            secret: process.env.JWT_SECRET,
            cookie: {
                cookieName: 'jwtToken',
                signed: false,
            }
        });

        fastify.register(require('@fastify/multipart'), {attachFieldsToBody: true, preservePath: true});
        function flattenFormData(req, reply, done) {
            // Check if the request is multipart form data
            if (req.isMultipart()) {
                // Flatten the fields object
                req.body = Object.fromEntries(
                    Object.entries(req.body).map(([key, value]) => {
                        // if (typeof value === 'object' && value.type === 'file') {
                        const item = Array.isArray(value) ? value[0] : value;

                        if (item && typeof item === 'object' && item.type === 'file') {
                            // Skip file fields
                            return [key, item];
                        } else {
                            // Flatten field value
                            return [key, item ? item.value : undefined];
                        }
                    })
                );
            }
            done();
        }
        
        // Use the custom middleware
        fastify.addHook('preHandler', flattenFormData);
        fastify.register(require('@fastify/cookie'));
        // fastify.register(require('./src/middleware/auth-middleware'));
        fastify.register(require('./src/routes/api'), {
            prefix: '/api/cohr'
        });

        await fastify.listen({ port: 8021, host: ip }, (err) => {
            if (err) {
                fastify.log.error(err);
                process.exit(1);
            }
        });
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

module.exports = {
    createServer,
};