import React from "react"
import "./Home.css"

const Home: React.FC = () => {
    return (
        <div className="container-fluid home-bg w-100">
            <div className="row h-75">
                <div className="col">
                    <div className="w-25 h-100 ml-30p mt-5p bg-light rounded shadow opacity-75">
                        <div className="col d-flex">
                            <h3>ChessRl</h3>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}


export default Home;
