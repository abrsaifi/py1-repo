module.exports = {
  presets: [['babel-preset-react-native', {useTransformReactJSXExperimental: true}]],
  plugins: [
    [
      '@babel/plugin-transform-react-jsx',
      {
        runtime: 'automatic',
      },
    ],
  ],
};
