import { Flex, Box } from "@chakra-ui/react";
import React, { useState } from "react";
import Divider from "../components/Divider";
import Footer from "../components/Footer";
import Header from "../components/Header";
import Messages from "../components/Messages";
import axios from "axios";
import SvgPopupButton from "../components/PopUpSvg";

const Chat = () => {
  const [messages, setMessages] = useState([
    { from: "VerbBot", text: "Hi, My Name is VerbBot" },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [currentInputMessage, setCurrentInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = () => {
    if (!inputMessage.trim().length) {
      return;
    }
    const data = inputMessage;
    const synth = window.speechSynthesis;

    if (synth.speaking) {
      console.error("speechSynthesis.speaking");
      return;
    }

    setMessages((old) => [
      ...old,
      {
        from: "me",
        text: <SvgPopupButton data={data} />,
      },
    ]);
    setInputMessage("");
    setIsLoading(true);

    axios
      .post("http://localhost:5000/api/sendMessage", { message: data })
      .then((response) => {
        const response_message = response.data["message"];
        const explanation = response.data["explanation"]
          .split("|")
          .map((line, index) => {
            const colors = ["#f6e58d", "#ffbe76", "#ff7979"]; // Add more colors as needed
            const backgroundColor = colors[index % colors.length];

            const lineStyle = {
              backgroundColor,
              padding: "5px",
              fontWeight: "bold",
            };
            return (
              <div key={index} style={lineStyle}>
                {line}
              </div>
            );
          });
        setCurrentInputMessage(explanation);
        console.log(explanation);
        console.log(response_message);
        setMessages((old) => [
          ...old,
          { from: "VerbBot", text: response_message },
        ]);
        if (
          navigator.onLine &&
          response_message !== "" &&
          response_message.length < 164
        ) {
          const utterance = new SpeechSynthesisUtterance(response_message);
          const voices = speechSynthesis.getVoices();
          utterance.voice = voices.find(
            (voice) => voice.name === "Google UK English Female"
          );
          utterance.rate = 0.9;
          synth.speak(utterance);
        }
        setIsLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setMessages((old) => [...old, { from: "VerbBot", text: error }]);
        setIsLoading(false);
      });
  };

  return (
    <Flex w="100%" h="100vh" justify="center" align="center">
      <Flex w="60%" h="90%" flexDir="column">
        <Header isLoading={isLoading} />
        <Divider />
        <Messages messages={messages} />
        <Divider />
        <Footer
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          handleSendMessage={handleSendMessage}
        />
      </Flex>
      <Box width="200px" h="300px" bg="gray.200" p="3" ml="6">
        <strong style={{ fontSize: "20px" }}>
          Why did I get this response?
        </strong>
        {currentInputMessage}
      </Box>
    </Flex>
  );
};

export default Chat;
