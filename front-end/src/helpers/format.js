const getCurrentTimestamp = () => {
    return new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/(\d+)\/(\d+)\/(\d+), /, '$3-$1-$2 ');
}

const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/(\d+)\/(\d+)\/(\d+), /, '$3-$1-$2 ');
}

const getCurrentDate = (date = null) => {
    return date === null ? new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Jakarta' }).replace(/\//g, '-') : new Date(date).toLocaleDateString('en-CA', { timeZone: 'Asia/Jakarta' }).split('-').reverse().join('-');
}

const getIndonesiaDate = (date = null) => {
    return date === null ? new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date()) : new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(date));
}

const getIndonesiaDateTime = (date) => {
    return new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: false }).format(new Date(date)).replaceAll(' pukul', ',').replaceAll('.', ':');
}

export default { getCurrentTimestamp, getCurrentDate, formatTimestamp, getIndonesiaDate, getIndonesiaDateTime }