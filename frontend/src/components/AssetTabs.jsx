import {
  Box,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from "@chakra-ui/react";

const AssetTabs = () => {
  const bgColor = useColorModeValue("gray.100", "gray.700");
  const activeTabBg = useColorModeValue("white", "gray.800");
  const inactiveTabColor = useColorModeValue("gray.600", "gray.400");
  const activeTabColor = useColorModeValue("gray.800", "white");
  const panelBg = useColorModeValue("white", "gray.800");
  const panelColor = useColorModeValue("gray.800", "gray.200");

  return (
    <Tabs variant="unstyled" isFitted>
      <TabList mb="1em" bg={bgColor} borderRadius="lg">
        <Tab
          _selected={{ color: activeTabColor, bg: activeTabBg }}
          color={inactiveTabColor}
          borderTopRadius="lg"
        >
          One
        </Tab>
      </TabList>
      <TabPanels bg={panelBg} borderRadius="lg" p={4}>
        <TabPanel>
          <p color={panelColor}>one!</p>
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
};

export default AssetTabs;
