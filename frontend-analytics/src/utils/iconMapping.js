/**
 * Icon Mapping Utility
 * Maps all Font Awesome, Bootstrap, and custom icons to react-icons equivalents
 * Supports multiple icon pack sources: fa (Font Awesome), bs (Bootstrap), fi (Feather), etc.
 */

// Font Awesome → react-icons/fa mappings
export const fontAwesomeMap = {
  // Navigation & UI
  'fas fa-home': { pack: 'fa', name: 'FaHome' },
  'fas fa-chart-bar': { pack: 'fa', name: 'FaChartBar' },
  'fas fa-chart-pie': { pack: 'fa', name: 'FaChartPie' },
  'fas fa-chart-line': { pack: 'fa', name: 'FaChartLine' },
  'fas fa-chart-area': { pack: 'fa', name: 'FaChartArea' },
  'fas fa-cube': { pack: 'fa', name: 'FaCube' },
  'fas fa-cubes': { pack: 'fa', name: 'FaCubes' },
  'fas fa-users': { pack: 'fa', name: 'FaUsers' },
  'fas fa-user': { pack: 'fa', name: 'FaUser' },
  'fas fa-user-circle': { pack: 'fa', name: 'FaUserCircle' },
  'fas fa-user-tie': { pack: 'fa', name: 'FaUserTie' },
  'fas fa-user-cog': { pack: 'fa', name: 'FaUserCog' },
  'fas fa-stream': { pack: 'fa', name: 'FaStream' },
  'fas fa-credit-card': { pack: 'fa', name: 'FaCreditCard' },
  'fas fa-lock': { pack: 'fa', name: 'FaLock' },
  'fas fa-unlock': { pack: 'fa', name: 'FaUnlock' },
  'fas fa-clipboard-list': { pack: 'fa', name: 'FaClipboardList' },
  'fas fa-plug': { pack: 'fa', name: 'FaPlug' },
  'fas fa-search': { pack: 'fa', name: 'FaSearch' },
  'fas fa-search-plus': { pack: 'fa', name: 'FaSearchPlus' },
  'fas fa-heartbeat': { pack: 'fa', name: 'FaHeartbeat' },
  'fas fa-heart': { pack: 'fa', name: 'FaHeart' },
  'fas fa-calendar': { pack: 'fa', name: 'FaCalendar' },
  'fas fa-th': { pack: 'fa', name: 'FaTh' },
  'fas fa-tachometer-alt': { pack: 'fa', name: 'FaTachometerAlt' },
  'fas fa-bell': { pack: 'fa', name: 'FaBell' },
  'fas fa-bell-slash': { pack: 'fa', name: 'FaBellSlash' },
  'fas fa-sliders-h': { pack: 'fa', name: 'FaSlidersH' },
  'fas fa-brain': { pack: 'fa', name: 'FaBrain' },
  'fas fa-microchip': { pack: 'fa', name: 'FaMicrochip' },
  'fas fa-database': { pack: 'fa', name: 'FaDatabase' },
  'fas fa-shield-alt': { pack: 'fa', name: 'FaShieldAlt' },
  'fas fa-cogs': { pack: 'fa', name: 'FaCogs' },
  'fas fa-cog': { pack: 'fa', name: 'FaCog' },
  'fas fa-file-alt': { pack: 'fa', name: 'FaFileAlt' },
  'fas fa-file': { pack: 'fa', name: 'FaFile' },
  'fas fa-folder': { pack: 'fa', name: 'FaFolder' },
  'fas fa-trash': { pack: 'fa', name: 'FaTrash' },
  'fas fa-download': { pack: 'fa', name: 'FaDownload' },
  'fas fa-upload': { pack: 'fa', name: 'FaUpload' },
  'fas fa-arrow-right': { pack: 'fa', name: 'FaArrowRight' },
  'fas fa-arrow-left': { pack: 'fa', name: 'FaArrowLeft' },
  'fas fa-arrow-up': { pack: 'fa', name: 'FaArrowUp' },
  'fas fa-arrow-down': { pack: 'fa', name: 'FaArrowDown' },
  'fas fa-chevron-right': { pack: 'fa', name: 'FaChevronRight' },
  'fas fa-chevron-left': { pack: 'fa', name: 'FaChevronLeft' },
  'fas fa-chevron-up': { pack: 'fa', name: 'FaChevronUp' },
  'fas fa-chevron-down': { pack: 'fa', name: 'FaChevronDown' },
  'fas fa-check': { pack: 'fa', name: 'FaCheck' },
  'fas fa-check-circle': { pack: 'fa', name: 'FaCheckCircle' },
  'fas fa-times': { pack: 'fa', name: 'FaTimes' },
  'fas fa-times-circle': { pack: 'fa', name: 'FaTimesCircle' },
  'fas fa-exclamation-triangle': { pack: 'fa', name: 'FaExclamationTriangle' },
  'fas fa-exclamation-circle': { pack: 'fa', name: 'FaExclamationCircle' },
  'fas fa-info-circle': { pack: 'fa', name: 'FaInfoCircle' },
  'fas fa-question-circle': { pack: 'fa', name: 'FaQuestionCircle' },
  'fas fa-plus': { pack: 'fa', name: 'FaPlus' },
  'fas fa-minus': { pack: 'fa', name: 'FaMinus' },
  'fas fa-spinner': { pack: 'fa', name: 'FaSpinner' },
  'fas fa-refresh': { pack: 'fa', name: 'FaSync' },
  'fas fa-sync': { pack: 'fa', name: 'FaSync' },
  'fas fa-loading': { pack: 'fa', name: 'FaSpinner' },
  'fas fa-save': { pack: 'fa', name: 'FaSave' },
  'fas fa-redo': { pack: 'fa', name: 'FaRedo' },
  'fas fa-eye': { pack: 'fa', name: 'FaEye' },
  'fas fa-eye-slash': { pack: 'fa', name: 'FaEyeSlash' },
  'fas fa-sign-out-alt': { pack: 'fa', name: 'FaSignOutAlt' },
  'fas fa-sign-in-alt': { pack: 'fa', name: 'FaSignInAlt' },
  'fas fa-star': { pack: 'fa', name: 'FaStar' },
  'fas fa-star-half-alt': { pack: 'fa', name: 'FaStarHalfAlt' },
  'fas fa-github': { pack: 'fa', name: 'FaGithub' },
  'fas fa-gitlab': { pack: 'fa', name: 'FaGitlab' },
  'fas fa-google': { pack: 'fa', name: 'FaGoogle' },
  'fas fa-linkedin': { pack: 'fa', name: 'FaLinkedin' },
  'fas fa-twitter': { pack: 'fa', name: 'FaTwitter' },
  'fas fa-facebook': { pack: 'fa', name: 'FaFacebook' },
  'fas fa-exchange-alt': { pack: 'fa', name: 'FaExchangeAlt' },
  'fas fa-filter': { pack: 'fa', name: 'FaFilter' },
  'fas fa-sort': { pack: 'fa', name: 'FaSort' },
  'fas fa-list': { pack: 'fa', name: 'FaList' },
  'fas fa-bars': { pack: 'fa', name: 'FaBars' },
  'fas fa-ban': { pack: 'fa', name: 'FaBan' },
  'fas fa-stop': { pack: 'fa', name: 'FaStop' },
  'fas fa-play': { pack: 'fa', name: 'FaPlay' },
  'fas fa-pause': { pack: 'fa', name: 'FaPause' },
  'fas fa-music': { pack: 'fa', name: 'FaMusic' },
  'fas fa-video': { pack: 'fa', name: 'FaVideo' },
  'fas fa-image': { pack: 'fa', name: 'FaImage' },
  'fas fa-flask': { pack: 'fa', name: 'FaFlask' },
  'fas fa-flask-flask': { pack: 'fa', name: 'FaFlask' },
};

// Bootstrap Icons → react-icons/bs mappings
export const bootstrapIconMap = {
  'bi bi-file': { pack: 'bs', name: 'BsFile' },
  'bi bi-file-pdf': { pack: 'bs', name: 'BsFilePdf' },
  'bi bi-file-image': { pack: 'bs', name: 'BsFileImage' },
  'bi bi-file-text': { pack: 'bs', name: 'BsFileText' },
  'bi bi-file-word': { pack: 'bs', name: 'BsFileWord' },
  'bi bi-file-excel': { pack: 'bs', name: 'BsFileExcel' },
  'bi bi-filetype-pdf': { pack: 'bs', name: 'BsFilePdf' },
  'bi bi-filetype-doc': { pack: 'bs', name: 'BsFileWord' },
  'bi bi-filetype-xls': { pack: 'bs', name: 'BsFileExcel' },
  'bi bi-filetype-ppt': { pack: 'bs', name: 'BsFileText' },
  'bi bi-sun': { pack: 'bs', name: 'BsSun' },
  'bi bi-moon': { pack: 'bs', name: 'BsMoon' },
  'bi bi-cloud': { pack: 'bs', name: 'BsCloud' },
  'bi bi-cloud-plus': { pack: 'bs', name: 'BsCloudPlus' },
  'bi bi-box': { pack: 'bs', name: 'BsBox' },
};

// Emoji → react-icons/fi mappings
export const emojiIconMap = {
  '⚡': { pack: 'fi', name: 'FiZap', label: 'Lightning' },
  '🔒': { pack: 'fi', name: 'FiLock', label: 'Lock' },
  '📱': { pack: 'fi', name: 'FiSmartphone', label: 'Mobile' },
  '🎯': { pack: 'fi', name: 'FiTarget', label: 'Target' },
  '☁️': { pack: 'fi', name: 'FiCloud', label: 'Cloud' },
  '💰': { pack: 'fi', name: 'FiDollarSign', label: 'Money' },
  '📊': { pack: 'fi', name: 'FiBarChart2', label: 'Bar Chart' },
  '📈': { pack: 'fi', name: 'FiTrendingUp', label: 'Trending' },
  '📉': { pack: 'fi', name: 'FiTrendingDown', label: 'Decline' },
  '🔍': { pack: 'fi', name: 'FiSearch', label: 'Search' },
  '📅': { pack: 'fi', name: 'FiCalendar', label: 'Calendar' },
  '⚙️': { pack: 'fi', name: 'FiSettings', label: 'Settings' },
  '🔔': { pack: 'fi', name: 'FiBell', label: 'Bell' },
  '💾': { pack: 'fi', name: 'FiSave', label: 'Save' },
  '🔌': { pack: 'fi', name: 'FiActivity', label: 'Activity' },
  '👥': { pack: 'fi', name: 'FiUsers', label: 'Users' },
  '👔': { pack: 'fi', name: 'FiAward', label: 'Award' },
  '🎭': { pack: 'fi', name: 'FiFilter', label: 'Filter' },
  '📋': { pack: 'fi', name: 'FiClipboard', label: 'Clipboard' },
  '📡': { pack: 'fi', name: 'FiWifi', label: 'Wifi' },
  '📑': { pack: 'fi', name: 'FiBook', label: 'Book' },
  '📝': { pack: 'fi', name: 'FiEdit', label: 'Edit' },
  '📄': { pack: 'fi', name: 'FiFile', label: 'File' },
  '🖼️': { pack: 'fi', name: 'FiImage', label: 'Image' },
  '📹': { pack: 'fi', name: 'FiVideo', label: 'Video' },
  '🎵': { pack: 'fi', name: 'FiMusic', label: 'Music' },
  '🗜️': { pack: 'fi', name: 'FiMinimize2', label: 'Compress' },
  '📐': { pack: 'fi', name: 'FiSliders', label: 'Sliders' },
  '🔄': { pack: 'fi', name: 'FiRefreshCw', label: 'Refresh' },
  '✅': { pack: 'fi', name: 'FiCheck', label: 'Check' },
  '❌': { pack: 'fi', name: 'FiX', label: 'Close' },
  '⚠️': { pack: 'fi', name: 'FiAlertTriangle', label: 'Warning' },
  '📦': { pack: 'fi', name: 'FiBox', label: 'Package' },
  '🚀': { pack: 'fi', name: 'FiArrowUpRight', label: 'Launch' },
  '📁': { pack: 'fi', name: 'FiFolder', label: 'Folder' },
  '📧': { pack: 'fi', name: 'FiMail', label: 'Email' },
  '🔗': { pack: 'fi', name: 'FiLink', label: 'Link' },
  '✂️': { pack: 'fi', name: 'FiScissors', label: 'Scissors' },
  '🖨️': { pack: 'fi', name: 'FiPrinter', label: 'Printer' },
  '🌐': { pack: 'fi', name: 'FiGlobe', label: 'Globe' },
  '📫': { pack: 'fi', name: 'FiInbox', label: 'Inbox' },
  '💿': { pack: 'fi', name: 'FiDisc', label: 'Disc' },
  '✨': { pack: 'fi', name: 'FiStar', label: 'Star' },
  '✓': { pack: 'fi', name: 'FiCheck', label: 'Check' },
  '🔐': { pack: 'fi', name: 'FiLock', label: 'Lock' },
  '🔓': { pack: 'fi', name: 'FiUnlock', label: 'Unlock' },
  '🎬': { pack: 'fi', name: 'FiFilm', label: 'Film' },
  '🎞️': { pack: 'fi', name: 'FiFilm', label: 'Film' },
  '📊': { pack: 'fi', name: 'FiBarChart2', label: 'Chart' },
  '📸': { pack: 'fi', name: 'FiCamera', label: 'Camera' },
  '🖥️': { pack: 'fi', name: 'FiMonitor', label: 'Monitor' },
  '⏱️': { pack: 'fi', name: 'FiClock', label: 'Clock' },
  '🏆': { pack: 'fi', name: 'FiAward', label: 'Trophy' },
  '🛡️': { pack: 'fi', name: 'FiShield', label: 'Shield' },
  '🎨': { pack: 'fi', name: 'FiFeather', label: 'Palette' },
  '🤖': { pack: 'fi', name: 'FiZap', label: 'Robot' },
  '🧠': { pack: 'fi', name: 'FiCpu', label: 'Brain' },
  '💬': { pack: 'fi', name: 'FiMessageCircle', label: 'Chat' },
  '🔥': { pack: 'fi', name: 'FiZap', label: 'Fire' },
  '📍': { pack: 'fi', name: 'FiMapPin', label: 'Location' },
  '🌳': { pack: 'fi', name: 'FiFilter', label: 'Tree' },
  '🔀': { pack: 'fi', name: 'FiShuffle', label: 'Shuffle' },
  '🆕': { pack: 'fi', name: 'FiPlus', label: 'New' },
  '🟢': { pack: 'fi', name: 'FiCheckCircle', label: 'Online' },
  '⚠️': { pack: 'fi', name: 'FiAlertCircle', label: 'Alert' },
  '🦠': { pack: 'fi', name: 'FiZap', label: 'Virus' },
  '🍚': { pack: 'fi', name: 'FiPackage', label: 'Package' },
  '📚': { pack: 'fi', name: 'FiBook', label: 'Books' },
};

// Get react-icons import from Font Awesome class
export const getReactIconFromFontAwesome = (faClass) => {
  return fontAwesomeMap[faClass] || null;
};

// Get react-icons import from Bootstrap class
export const getReactIconFromBootstrap = (bsClass) => {
  return bootstrapIconMap[bsClass] || null;
};

// Get react-icons import from Emoji
export const getReactIconFromEmoji = (emoji) => {
  return emojiIconMap[emoji] || null;
};

// Get all unique icon classes from Font Awesome mappings
export const getAllFontAwesomeClasses = () => {
  return Object.keys(fontAwesomeMap);
};

// Get all unique icon classes from Bootstrap mappings
export const getAllBootstrapClasses = () => {
  return Object.keys(bootstrapIconMap);
};

// Get all unique emojis from emoji mappings
export const getAllEmojis = () => {
  return Object.keys(emojiIconMap);
};

export default {
  fontAwesomeMap,
  bootstrapIconMap,
  emojiIconMap,
  getReactIconFromFontAwesome,
  getReactIconFromBootstrap,
  getReactIconFromEmoji,
  getAllFontAwesomeClasses,
  getAllBootstrapClasses,
  getAllEmojis,
};
