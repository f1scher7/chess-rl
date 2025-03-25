import React from 'react'


const Footer: React.FC = () => {
    return (
        <div className="bg-dark rounded-bottom-2 py-3">
            <div className="container d-flex flex-column justify-content-center align-items-center gap-3">
                <img className="w-25" src="/assets/fischer-logos/fischer-logo.png" alt="Maksymilian Fischer" onContextMenu={ (e) => e.preventDefault() }/>
                <span className="text-white mb-0">© 2025 Maksymilian Fischer. All rights reserved.</span>
            </div>
        </div>
    );
};


export default Footer;
