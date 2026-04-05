const fastify = require("fastify")({ logger: true });
const fastifyCors = require("@fastify/cors");

// const ip = "0.0.0.0";
const ip = "172.17.200.48";

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
                        if (typeof value === 'object' && value.type === 'file') {
                            // Skip file fields
                            return [key, value];
                        } else {
                            // Flatten field value
                            return [key, value.value];
                        }
                    })
                );
            }
            done();
        }
        
        // Use the custom middleware
        fastify.addHook('preHandler', flattenFormData);
        fastify.register(require('@fastify/cookie'));
        fastify.register(require('./src/middleware/auth-middleware'));
        fastify.register(require('./src/routes/api'), {
            prefix: '/api/nurse-education-portal'
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