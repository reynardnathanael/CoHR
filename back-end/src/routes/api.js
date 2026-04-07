const UserController = require("../controllers/user.controller");
// const PostController = require("../controllers/post.controller");
// const CategoryController = require("../controllers/category.controller");
// const checkUserRole = require('../middleware/auth-role');

module.exports = async (fastify) => {
    // fastify.register((user, opts, done) => {
    //     user.addHook('preValidation', fastify.authenticate);
    //     user.addHook('preValidation', checkUserRole(['1']));

    //     // user
    //     // user.get(`/user/all`, UserController.all);
    //     // user.post(`/user/register`, UserController.register);
    //     // user.post(`/user/delete`, UserController.deleteUser);
    //     // user.post(`/user/reset-default`, UserController.resetPasswordDefault);
    //     user.post('/user/view-reader', UserController.viewPostUsers);

    //     // category
    //     user.post(`/category/create`, CategoryController.create);
    //     user.post(`/category/update`, CategoryController.update);
    //     user.post(`/category/delete`, CategoryController.delete);
    //     user.get(`/category/summary`, CategoryController.summary);

    //     // post
    //     user.post(`/post/create`, PostController.createPostFile);
    //     user.post(`/post/update`, PostController.updatePost);
    //     user.get(`/post/download-file/:id`, PostController.downloadFile);

    //     done();
    // });

    // fastify.register((user, opts, done) => {
    //     user.addHook('preValidation', fastify.authenticate);

    //     // user
    //     user.post('/user/logout', UserController.logout);
    //     user.post('/user/add-view', UserController.createPostUser);
    //     // user.post(`/user/reset-password`, UserController.resetPassword);

    //     // post
    //     user.get(`/post/:id`, PostController.all);
    //     user.get(`/post/detail/:id`, PostController.detail);
    //     user.get(`/post/get-file/:id`, PostController.getFile);

    //     // category
    //     user.get(`/category/all`, CategoryController.all);
    //     user.get(`/category/:id`, CategoryController.detail);

    //     done();
    // });

    // user
    fastify.post(`/user/register`, UserController.register);
}