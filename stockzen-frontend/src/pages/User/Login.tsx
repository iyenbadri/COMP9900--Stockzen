import LoginForm from 'components/User/LoginForm';
import { UserContext } from 'contexts/UserContext';
import React, { FC, useContext, useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import styles from './Login.module.css';

const Login: FC = () => {
  const { isAuthenticated, authenticate } = useContext(UserContext);
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const history = useHistory();

  useEffect(() => {
    if (isAuthenticated) {
      history.replace('/portfolio');
    }
  }, [history, isAuthenticated]);

  const doAuthen = () => {
    authenticate();
    history.push('/portfolio');
  };

  return (
    <div className={styles.formWrapper}>
      {!isAuthenticated && (
        <LoginForm
          onLoginSuccess={(email, password) => {
            setEmail(email);
            setPassword(password);
            doAuthen();
          }}></LoginForm>
      )}

    </div >
  );
};

export default Login;
