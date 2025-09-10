import React from 'react';
import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'react-bootstrap';


type GameOverDialogProps = {
    show: boolean
    resultText: string,
    handleReset: () => void,
    handleClose: () => void,
}

const GameOverDialog: React.FC<GameOverDialogProps> = ({ show, resultText, handleReset, handleClose }: GameOverDialogProps) => {
    const handleRematch = () => {
        handleClose();
        handleReset();
    };

    return (
        <Modal
            show={show}
            onHide={handleClose}
            backdrop="static"
            keyboard={false}
        >
            <ModalHeader closeButton>
                <Modal.Title>
                    <h4>Game over</h4>
                </Modal.Title>
            </ModalHeader>
            <ModalBody>
                <h5>{resultText}</h5>
            </ModalBody>
            <ModalFooter>
                <Button variant="secondary" onClick={handleClose}>
                    Review Game
                </Button>
                <Button variant="dark" onClick={handleRematch}>
                    Rematch
                </Button>
            </ModalFooter>
        </Modal>
    );
};

export default GameOverDialog;
