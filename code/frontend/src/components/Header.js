import React, { useState, useEffect } from "react";
import { Flex, Avatar, AvatarBadge, Text } from "@chakra-ui/react";
import akaneico from "./akane.svg";

const Header = ({ isLoading }) => {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch("http://localhost:5000");
        if (response.ok) {
          setIsOnline(true);
        } else {
          setIsOnline(false);
        }
      } catch (error) {
        setIsOnline(false);
      }
    };

    // Call the function to check server status when the component mounts
    checkServerStatus();

    // Optionally, you can set up a periodic check to keep verifying the server status.
    // For example, every 5 seconds:
    const interval = setInterval(checkServerStatus, 15000);

    // Clean up the interval when the component unmounts
    return () => clearInterval(interval);
  }, []);

  return (
    <Flex w="100%">
      <Avatar size="lg" name="Dan Abrahmov" src={akaneico}>
        <AvatarBadge boxSize="1.25em" bg="green.500" />
      </Avatar>
      <Flex flexDirection="column" mx="5" justify="center">
        <Text fontSize="lg" fontWeight="bold">
          VerbBot
        </Text>
        <div>
          {isOnline ? (
            <Text color="green.500">{isLoading ? "Typing..." : "Online"}</Text>
          ) : (
            <Text color="red.500">Offline</Text>
          )}
        </div>
      </Flex>
    </Flex>
  );
};

export default Header;
