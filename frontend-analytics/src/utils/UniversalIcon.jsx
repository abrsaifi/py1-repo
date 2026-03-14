/**
 * React Icons Wrapper Component
 * Dynamically renders icons from different react-icons packs
 */
import React from 'react';
import {
  FaArrowDown,
  FaArrowLeft,
  FaArrowRight,
  FaArrowUp,
  FaBan,
  FaBars,
  FaBell,
  FaBellSlash,
  FaBrain,
  FaCalendar,
  FaChartArea,
  FaChartBar,
  FaChartLine,
  FaChartPie,
  FaCheck,
  FaCheckCircle,
  FaChevronDown,
  FaChevronLeft,
  FaChevronRight,
  FaChevronUp,
  FaClipboardList,
  FaCog,
  FaCogs,
  FaCreditCard,
  FaCube,
  FaCubes,
  FaDatabase,
  FaDownload,
  FaExchangeAlt,
  FaExclamationCircle,
  FaExclamationTriangle,
  FaEye,
  FaEyeSlash,
  FaFacebook,
  FaFile,
  FaFileAlt,
  FaFilter,
  FaFlask,
  FaFolder,
  FaGithub,
  FaGitlab,
  FaGoogle,
  FaHeart,
  FaHeartbeat,
  FaHome,
  FaImage,
  FaInfoCircle,
  FaLinkedin,
  FaList,
  FaLock,
  FaMicrochip,
  FaMinus,
  FaMusic,
  FaPause,
  FaPlay,
  FaPlug,
  FaPlus,
  FaQuestionCircle,
  FaRedo,
  FaSave,
  FaSearch,
  FaSearchPlus,
  FaShieldAlt,
  FaSignInAlt,
  FaSignOutAlt,
  FaSlidersH,
  FaSort,
  FaSpinner,
  FaStar,
  FaStarHalfAlt,
  FaStop,
  FaStream,
  FaSync,
  FaTachometerAlt,
  FaTh,
  FaTimes,
  FaTimesCircle,
  FaTrash,
  FaTwitter,
  FaUnlock,
  FaUpload,
  FaUser,
  FaUserCircle,
  FaUserCog,
  FaUserTie,
  FaUsers,
  FaVideo,
} from 'react-icons/fa';
import {
  BsBox,
  BsCloud,
  BsCloudPlus,
  BsFile,
  BsFileExcel,
  BsFileImage,
  BsFilePdf,
  BsFileText,
  BsFileWord,
  BsMoon,
  BsSun,
} from 'react-icons/bs';
import {
  FiActivity,
  FiAlertCircle,
  FiAlertTriangle,
  FiArrowUpRight,
  FiAward,
  FiBarChart2,
  FiBell,
  FiBook,
  FiBox,
  FiCalendar,
  FiCamera,
  FiCheck,
  FiCheckCircle,
  FiClipboard,
  FiClock,
  FiCloud,
  FiCpu,
  FiDisc,
  FiDollarSign,
  FiEdit,
  FiFeather,
  FiFile,
  FiFilm,
  FiFilter,
  FiFolder,
  FiGlobe,
  FiImage,
  FiInbox,
  FiLink,
  FiLock,
  FiMail,
  FiMapPin,
  FiMessageCircle,
  FiMinimize2,
  FiMonitor,
  FiMusic,
  FiPackage,
  FiPlus,
  FiPrinter,
  FiRefreshCw,
  FiSave,
  FiScissors,
  FiSearch,
  FiSettings,
  FiShield,
  FiShuffle,
  FiSliders,
  FiSmartphone,
  FiStar,
  FiTarget,
  FiTrendingDown,
  FiTrendingUp,
  FiUnlock,
  FiUsers,
  FiVideo,
  FiWifi,
  FiX,
  FiZap,
} from 'react-icons/fi';
import iconMappingModule from './iconMapping';

const faIcons = {
  FaArrowDown,
  FaArrowLeft,
  FaArrowRight,
  FaArrowUp,
  FaBan,
  FaBars,
  FaBell,
  FaBellSlash,
  FaBrain,
  FaCalendar,
  FaChartArea,
  FaChartBar,
  FaChartLine,
  FaChartPie,
  FaCheck,
  FaCheckCircle,
  FaChevronDown,
  FaChevronLeft,
  FaChevronRight,
  FaChevronUp,
  FaClipboardList,
  FaCog,
  FaCogs,
  FaCreditCard,
  FaCube,
  FaCubes,
  FaDatabase,
  FaDownload,
  FaExchangeAlt,
  FaExclamationCircle,
  FaExclamationTriangle,
  FaEye,
  FaEyeSlash,
  FaFacebook,
  FaFile,
  FaFileAlt,
  FaFilter,
  FaFlask,
  FaFolder,
  FaGithub,
  FaGitlab,
  FaGoogle,
  FaHeart,
  FaHeartbeat,
  FaHome,
  FaImage,
  FaInfoCircle,
  FaLinkedin,
  FaList,
  FaLock,
  FaMicrochip,
  FaMinus,
  FaMusic,
  FaPause,
  FaPlay,
  FaPlug,
  FaPlus,
  FaQuestionCircle,
  FaRedo,
  FaSave,
  FaSearch,
  FaSearchPlus,
  FaShieldAlt,
  FaSignInAlt,
  FaSignOutAlt,
  FaSlidersH,
  FaSort,
  FaSpinner,
  FaStar,
  FaStarHalfAlt,
  FaStop,
  FaStream,
  FaSync,
  FaTachometerAlt,
  FaTh,
  FaTimes,
  FaTimesCircle,
  FaTrash,
  FaTwitter,
  FaUnlock,
  FaUpload,
  FaUser,
  FaUserCircle,
  FaUserCog,
  FaUserTie,
  FaUsers,
  FaVideo,
};

const bsIcons = {
  BsBox,
  BsCloud,
  BsCloudPlus,
  BsFile,
  BsFileExcel,
  BsFileImage,
  BsFilePdf,
  BsFileText,
  BsFileWord,
  BsMoon,
  BsSun,
};

const fiIcons = {
  FiActivity,
  FiAlertCircle,
  FiAlertTriangle,
  FiArrowUpRight,
  FiAward,
  FiBarChart2,
  FiBell,
  FiBook,
  FiBox,
  FiCalendar,
  FiCamera,
  FiCheck,
  FiCheckCircle,
  FiClipboard,
  FiClock,
  FiCloud,
  FiCpu,
  FiDisc,
  FiDollarSign,
  FiEdit,
  FiFeather,
  FiFile,
  FiFilm,
  FiFilter,
  FiFolder,
  FiGlobe,
  FiImage,
  FiInbox,
  FiLink,
  FiLock,
  FiMail,
  FiMapPin,
  FiMessageCircle,
  FiMinimize2,
  FiMonitor,
  FiMusic,
  FiPackage,
  FiPlus,
  FiPrinter,
  FiRefreshCw,
  FiSave,
  FiScissors,
  FiSearch,
  FiSettings,
  FiShield,
  FiShuffle,
  FiSliders,
  FiSmartphone,
  FiStar,
  FiTarget,
  FiTrendingDown,
  FiTrendingUp,
  FiUnlock,
  FiUsers,
  FiVideo,
  FiWifi,
  FiX,
  FiZap,
};

/**
 * Universal icon component that handles Font Awesome, Bootstrap, and Emoji icons
 * @param {string} icon - Font Awesome class (e.g., 'fas fa-home'), Bootstrap class (e.g., 'bi bi-file'), or emoji
 * @param {number} size - Icon size in pixels (default: 24)
 * @param {string} color - Icon color (default: 'currentColor')
 * @param {object} style - Additional inline styles
 * @param {string} className - Additional CSS classes
 */
export const UniversalIcon = ({ 
  icon, 
  size = 24, 
  color = 'currentColor',
  style = {},
  className = '',
  title = '',
  ...props
}) => {
  if (!icon) return null;

  // Handle Font Awesome icons
  if (icon.startsWith('fas ') || icon.startsWith('far ') || icon.startsWith('fal ') || icon.startsWith('fad ')) {
    const mapping = iconMappingModule.fontAwesomeMap[icon];
    if (mapping && mapping.pack === 'fa') {
      const IconComponent = faIcons[mapping.name];
      if (IconComponent) {
        return (
          <IconComponent 
            size={size} 
            color={color} 
            style={{...style, color, fill: color}}
            className={className}
            title={title}
            {...props}
          />
        );
      }
    }
  }

  // Handle Bootstrap icons
  if (icon.startsWith('bi ') || icon.startsWith('bi-')) {
    const mapping = iconMappingModule.bootstrapIconMap[icon];
    if (mapping && mapping.pack === 'bs') {
      const IconComponent = bsIcons[mapping.name];
      if (IconComponent) {
        return (
          <IconComponent 
            size={size} 
            color={color} 
            style={{...style, color, fill: color}}
            className={className}
            title={title}
            {...props}
          />
        );
      }
    }
  }

  // Handle Emoji icons - convert to appropriate Feather icon
  if (iconMappingModule.emojiIconMap[icon]) {
    const mapping = iconMappingModule.emojiIconMap[icon];
    if (mapping.pack === 'fi') {
      const IconComponent = fiIcons[mapping.name];
      if (IconComponent) {
        return (
          <IconComponent 
            size={size} 
            color={color}
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            style={{...style, color}}
            className={className}
            title={title || mapping.label}
            {...props}
          />
        );
      }
    }
  }

  // Fallback - return the original icon string (emoji or placeholder)
  return <span className={className} style={style} title={title}>{icon}</span>;
};

/**
 * Font Awesome icon component wrapper
 */
export const FontAwesomeIcon = ({ icon, size = 24, color = 'currentColor', ...props }) => {
  const mapping = iconMappingModule.fontAwesomeMap[icon];
  if (mapping && mapping.pack === 'fa') {
    const IconComponent = faIcons[mapping.name];
    if (IconComponent) {
      return <IconComponent size={size} color={color} {...props} />;
    }
  }
  return null;
};

/**
 * Bootstrap icon component wrapper
 */
export const BootstrapIcon = ({ icon, size = 24, color = 'currentColor', ...props }) => {
  const mapping = iconMappingModule.bootstrapIconMap[icon];
  if (mapping && mapping.pack === 'bs') {
    const IconComponent = bsIcons[mapping.name];
    if (IconComponent) {
      return <IconComponent size={size} color={color} {...props} />;
    }
  }
  return null;
};

/**
 * Emoji to Feather icon component wrapper
 */
export const EmojiIcon = ({ emoji, size = 24, color = 'currentColor', ...props }) => {
  const mapping = iconMappingModule.emojiIconMap[emoji];
  if (mapping && mapping.pack === 'fi') {
    const IconComponent = fiIcons[mapping.name];
    if (IconComponent) {
      const featherStyle = {
        color: color,
        stroke: color,
        fill: color,
        strokeWidth: 2,
        strokeLinecap: 'round',
        strokeLinejoin: 'round'
      };
      return <IconComponent size={size} color={color} stroke={color} fill={color} style={featherStyle} title={mapping.label} {...props} />;
    }
  }
  return <span {...props}>{emoji}</span>;
};

/**
 * Render icon safely with className
 * Extracts i tags and replaces with UniversalIcon components
 */
export const safeRenderIcon = (iconString, size = 24, color = 'currentColor') => {
  return <UniversalIcon icon={iconString} size={size} color={color} />;
};

export default {
  UniversalIcon,
  FontAwesomeIcon,
  BootstrapIcon,
  EmojiIcon,
  safeRenderIcon,
};
