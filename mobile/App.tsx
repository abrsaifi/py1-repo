import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/FontAwesome6';

// Screens
import LoginScreen from './src/screens/auth/LoginScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';
import DashboardScreen from './src/screens/dashboard/DashboardScreen';
import DuplicateRemoverScreen from './src/screens/features/DuplicateRemoverScreen';
import DataValidatorScreen from './src/screens/features/DataValidatorScreen';
import PDFExportScreen from './src/screens/features/PDFExportScreen';
import ReportGeneratorScreen from './src/screens/features/ReportGeneratorScreen';
import AnalyticsScreen from './src/screens/analytics/AnalyticsScreen';
import SettingsScreen from './src/screens/settings/SettingsScreen';
import ProfileScreen from './src/screens/settings/ProfileScreen';
import SplashScreen from './src/screens/auth/SplashScreen';

// Types
export type RootStackParamList = {
  Splash: undefined;
  Auth: undefined;
  MainApp: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type MainStackParamList = {
  Dashboard: undefined;
  DuplicateRemover: undefined;
  DataValidator: undefined;
  PDFExport: undefined;
  ReportGenerator: undefined;
};

export type TabsParamList = {
  Home: undefined;
  Tools: undefined;
  Analytics: undefined;
  Settings: undefined;
};

const RootStack = createNativeStackNavigator<RootStackParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const MainStack = createNativeStackNavigator<MainStackParamList>();
const Tab = createBottomTabNavigator<TabsParamList>();

// Auth Navigator
function AuthNavigator() {
  return (
    <AuthStack.Navigator
      screenOptions={{
        headerShown: false,
        animationEnabled: true,
      }}
    >
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
    </AuthStack.Navigator>
  );
}

// Home Stack Navigator
function HomeStackNavigator() {
  return (
    <MainStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#667eea',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <MainStack.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ headerTitle: '📄 DocPro' }}
      />
    </MainStack.Navigator>
  );
}

// Tools Stack Navigator
function ToolsStackNavigator() {
  return (
    <MainStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#667eea',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <MainStack.Screen
        name="DuplicateRemover"
        component={DuplicateRemoverScreen}
        options={{ headerTitle: '🔄 Duplicate Remover' }}
      />
      <MainStack.Screen
        name="DataValidator"
        component={DataValidatorScreen}
        options={{ headerTitle: '✅ Data Validator' }}
      />
      <MainStack.Screen
        name="PDFExport"
        component={PDFExportScreen}
        options={{ headerTitle: '📤 PDF Export' }}
      />
      <MainStack.Screen
        name="ReportGenerator"
        component={ReportGeneratorScreen}
        options={{ headerTitle: '📊 Report Generator' }}
      />
    </MainStack.Navigator>
  );
}

// Main App Navigator (Bottom Tabs)
function MainAppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName = 'home';
          
          switch (route.name) {
            case 'Home':
              iconName = 'house';
              break;
            case 'Tools':
              iconName = 'wrench';
              break;
            case 'Analytics':
              iconName = 'chart-line';
              break;
            case 'Settings':
              iconName = 'gear';
              break;
          }
          
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#667eea',
        tabBarInactiveTintColor: '#999',
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        tabBarStyle: {
          borderTopColor: '#e2e8f0',
          backgroundColor: '#f8f9ff',
          paddingBottom: 5,
          height: 60,
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeStackNavigator}
        options={{
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen
        name="Tools"
        component={ToolsStackNavigator}
        options={{
          tabBarLabel: 'Tools',
        }}
      />
      <Tab.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
}

// Root Navigator
export default function App() {
  const [state, dispatch] = React.useReducer(
    (prevState: { isLoading: boolean; isSignout: boolean; userToken: string | null }, action: any) => {
      switch (action.type) {
        case 'RESTORE_TOKEN':
          return {
            ...prevState,
            userToken: action.payload,
            isLoading: false,
          };
        case 'SIGN_IN':
          return {
            ...prevState,
            isSignout: false,
            userToken: action.payload,
          };
        case 'SIGN_OUT':
          return {
            ...prevState,
            isSignout: true,
            userToken: null,
          };
      }
    },
    {
      isLoading: true,
      isSignout: false,
      userToken: null,
    },
  );

  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const userToken = await AsyncStorage.getItem('userToken');
        dispatch({ type: 'RESTORE_TOKEN', payload: userToken });
      } catch (e) {
        // Restoring token failed
      }
    };

    bootstrapAsync();
  }, []);

  return (
    <NavigationContainer>
      <RootStack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        {state.isLoading ? (
          <RootStack.Screen name="Splash" component={SplashScreen} />
        ) : state.userToken == null ? (
          <RootStack.Screen
            name="Auth"
            component={AuthNavigator}
            options={{
              animationEnabled: false,
            }}
          />
        ) : (
          <RootStack.Screen
            name="MainApp"
            component={MainAppNavigator}
            options={{
              animationEnabled: false,
            }}
          />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
}
