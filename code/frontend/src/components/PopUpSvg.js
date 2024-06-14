import React, { useState } from "react";
import axios from "axios";
import Modal from "react-modal";

const SvgPopupButton = ({ data }) => {
  const [svg, setSvg] = useState("");
  const [showPopup, setShowPopup] = useState(false);

  const getDepTree = async (inputString) => {
    try {
      const response = await axios.post(
        "http://localhost:5000/api/getDepTree",
        { message: inputString }
      );
      setSvg(response.data["svg"]);
      setShowPopup(true);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <>
      <button onClick={() => getDepTree(data)}>{data}</button>
      <Modal
        isOpen={showPopup}
        onRequestClose={() => setShowPopup(false)}
        shouldCloseOnOverlayClick={false}
        ariaHideApp={false}
      >
        {/* <h2>Dependency Tree</h2> */}
        <button onClick={() => setShowPopup(false)}>Close</button>
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      </Modal>
    </>
  );
};

export default SvgPopupButton;
