const getCurrentTimestamp = () => {
    return new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/(\d+)\/(\d+)\/(\d+), /, '$3-$1-$2 ');
}

const getCurrentDate = () => {
    return new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Jakarta' }).replace(/\//g, '-');
}

const formatDateTime = () => {
    return new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/(\d+)\/(\d+)\/(\d+), (\d+):(\d+):(\d+)/, '$3$1$2_$4$5$6');
}

const generateFileTimestamp = () => {
    return `_${new Date().toLocaleString('en-CA', {timeZone: 'Asia/Jakarta', hour12: false}).replace(/[^\d]/g, '').slice(0, 14)}`;
}

// const addTimestampToFilename = filename => filename.replace(/(\.[^.]+)$/, `_${new Date().toLocaleString('en-CA', {timeZone: 'Asia/Jakarta', hour12: false}).replace(/[^\d]/g, '').slice(0, 14)}$1`);

const addTimestampToFilename = (filename, timestamp) => {
    return filename.replace(/(\.[^.]+)$/, `${timestamp}$1`);
}

const getExtension = (filename) => {
    const imageExt = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff", "ico", "heic"];
    const ext = filename.split('.').pop().toLowerCase();
    if (imageExt.includes(ext))
        return 'IMAGE';
    else
        return 'PDF';
}

module.exports = { getCurrentTimestamp, getCurrentDate, formatDateTime, generateFileTimestamp, addTimestampToFilename, getExtension };