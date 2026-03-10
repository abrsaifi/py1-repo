import React from 'react';
import { 
  FiFile, FiImage, FiFileText, FiMusic, FiVideo, FiZap, FiCheck, FiClock, FiAlertCircle, FiX, FiUser, FiUsers, FiLock, FiEye, FiBarChart2, FiTrendingUp, FiDownload, FiUpload, FiUserCheck, FiUserX, FiDatabase, FiFilter, FiTruck, FiPackage, FiCheckCircle, FiAlertTriangle, FiInfo, FiRefreshCw
} from 'react-icons/fi';

// File format icons
export const getFileFormatIcon = (format) => {
  const formatLower = format?.toLowerCase() || '';
  
  const iconMap = {
    // Document formats
    'pdf': <FiFileText size={14} />,
    'doc': <FiFileText size={14} />,
    'docx': <FiFileText size={14} />,
    'txt': <FiFileText size={14} />,
    'xlsx': <FiFile size={14} />,
    'xls': <FiFile size={14} />,
    'csv': <FiFile size={14} />,
    
    // Image formats
    'jpg': <FiImage size={14} />,
    'jpeg': <FiImage size={14} />,
    'png': <FiImage size={14} />,
    'gif': <FiImage size={14} />,
    'svg': <FiImage size={14} />,
    'webp': <FiImage size={14} />,
    'ico': <FiImage size={14} />,
    
    // Audio formats
    'mp3': <FiMusic size={14} />,
    'wav': <FiMusic size={14} />,
    'flac': <FiMusic size={14} />,
    'aac': <FiMusic size={14} />,
    
    // Video formats
    'mp4': <FiVideo size={14} />,
    'avi': <FiVideo size={14} />,
    'mov': <FiVideo size={14} />,
    'mkv': <FiVideo size={14} />,
    'webm': <FiVideo size={14} />,
    
    // Default
    'default': <FiFile size={14} />
  };
  
  return iconMap[formatLower] || iconMap['default'];
};

// Status badge icons
export const getStatusIcon = (status) => {
  const statusLower = status?.toLowerCase() || '';
  
  const iconMap = {
    'completed': <FiCheckCircle size={14} />,
    'success': <FiCheckCircle size={14} />,
    'done': <FiCheckCircle size={14} />,
    
    'processing': <FiZap size={14} />,
    'running': <FiZap size={14} />,
    'in-progress': <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />,
    'pending': <FiClock size={14} />,
    'queued': <FiClock size={14} />,
    'waiting': <FiClock size={14} />,
    
    'failed': <FiX size={14} />,
    'error': <FiAlertCircle size={14} />,
    'cancelled': <FiX size={14} />,
    
    'active': <FiCheckCircle size={14} />,
    'inactive': <FiX size={14} />,
    
    'warning': <FiAlertTriangle size={14} />,
    'info': <FiInfo size={14} />,
    
    'default': <FiFile size={14} />
  };
  
  return iconMap[statusLower] || iconMap['default'];
};

// Role badges icons
export const getRoleIcon = (role) => {
  const roleLower = role?.toLowerCase() || '';
  
  const iconMap = {
    'admin': <FiLock size={14} />,
    'administrator': <FiLock size={14} />,
    
    'manager': <FiBarChart2 size={14} />,
    'lead': <FiBarChart2 size={14} />,
    
    'analyst': <FiTrendingUp size={14} />,
    'data analyst': <FiTrendingUp size={14} />,
    
    'viewer': <FiEye size={14} />,
    'guest': <FiEye size={14} />,
    
    'user': <FiUser size={14} />,
    'member': <FiUser size={14} />,
    
    'default': <FiUser size={14} />
  };
  
  return iconMap[roleLower] || iconMap['default'];
};

// Plan/subscription badges
export const getPlanIcon = (plan) => {
  const planLower = plan?.toLowerCase() || '';
  
  const iconMap = {
    'free': <FiFilter size={14} />,
    'starter': <FiUpload size={14} />,
    'pro': <FiTrendingUp size={14} />,
    'premium': <FiZap size={14} />,
    'enterprise': <FiDatabase size={14} />,
    'business': <FiBarChart2 size={14} />,
    'default': <FiPackage size={14} />
  };
  
  return iconMap[planLower] || iconMap['default'];
};

// User status icons
export const getUserStatusIcon = (status) => {
  const statusLower = status?.toLowerCase() || '';
  
  const iconMap = {
    'active': <FiUserCheck size={14} />,
    'verified': <FiUserCheck size={14} />,
    'approved': <FiUserCheck size={14} />,
    
    'inactive': <FiUserX size={14} />,
    'pending': <FiClock size={14} />,
    'suspended': <FiLock size={14} />,
    'blocked': <FiX size={14} />,
    
    'default': <FiUser size={14} />
  };
  
  return iconMap[statusLower] || iconMap['default'];
};

// Generic badge with icon wrapper component
export const BadgeWithIcon = ({ icon, text, className = '', style = {} }) => {
  return (
    <span className={`badge-with-icon ${className}`} style={style}>
      <span className="badge-icon">{icon}</span>
      <span className="badge-text">{text}</span>
    </span>
  );
};

// Format badge component
export const FormatBadge = ({ format, style = {} }) => {
  return (
    <span className="format-badge" style={style}>
      <span className="badge-icon">{getFileFormatIcon(format)}</span>
      <span className="badge-text">{format}</span>
    </span>
  );
};

// Status badge component
export const StatusBadge = ({ status, text, style = {} }) => {
  return (
    <span className="status-badge" style={style}>
      <span className="badge-icon">{getStatusIcon(status)}</span>
      <span className="badge-text">{text}</span>
    </span>
  );
};

// Role badge component
export const RoleBadge = ({ role, style = {} }) => {
  return (
    <span className={`format-badge role-${role?.toLowerCase()}`} style={style}>
      <span className="badge-icon">{getRoleIcon(role)}</span>
      <span className="badge-text">{role}</span>
    </span>
  );
};

// Plan badge component
export const PlanBadge = ({ plan, style = {} }) => {
  return (
    <span className="format-badge" style={style}>
      <span className="badge-icon">{getPlanIcon(plan)}</span>
      <span className="badge-text">{plan}</span>
    </span>
  );
};
