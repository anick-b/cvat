import React from 'react';
import { useDispatch } from 'react-redux';
import { logoutAsync } from 'actions/auth-actions';
import Modal from 'antd/lib/modal';
import Button from 'antd/lib/button';
import Space from 'antd/lib/space';
import Text from 'antd/lib/typography/Text';
import { ExclamationCircleOutlined } from '@ant-design/icons';

interface TimeoutWarningModalProps {
    isOpen: boolean;
    onRequestClose: () => void;
    onLogout: () => void;
    remainingTime: number;
}

export const TimeoutWarningModal: React.FC<TimeoutWarningModalProps> = ({
    isOpen,
    onRequestClose,
    onLogout,
    remainingTime
}) => {
    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <Modal
            title={
                <Space>
                    <ExclamationCircleOutlined style={{ color: '#faad14' }} />
                    <Text strong>Session Timeout Warning</Text>
                </Space>
            }
            open={isOpen}
            onCancel={onRequestClose}
            footer={[
                <Button key="logout" danger onClick={onLogout}>
                    Log Off
                </Button>,
                <Button key="stay" type="primary" onClick={onRequestClose}>
                    Stay Logged In
                </Button>,
            ]}
            closable={false}
            maskClosable={false}
            keyboard={false}
            width={500}
        >
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Text>
                    Your session will expire in{' '}
                    <Text strong style={{ color: '#faad14', fontSize: '18px' }}>
                        {formatTime(remainingTime)}
                    </Text>{' '}
                    due to inactivity.
                </Text>
                <br />
                <br />
                <Text type="secondary">
                    Please choose to stay signed in or log off. Otherwise, you will be logged off automatically.
                </Text>
            </div>
        </Modal>
    );
};