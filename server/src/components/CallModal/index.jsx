/* third libs */
import React, { Children, useMemo } from "react";
import { FormattedMessage as Intl } from "react-intl";
import cn from "classnames";

/* material-ui */
import Model from "@comp/Model";
import Text from "@comp/Text";
import HeadLine from "@comp/HeadLine";
import Button from "@comp/Button";
import Loading from "src/icons/StatusIcon/Loading";
import Confirm from "src/icons/StatusIcon/Confirm";
import Success from "src/icons/StatusIcon/Success";
import ErrorIcon from "src/icons/StatusIcon/Error";

/* local components & methods */
import styles from "./styles.module.scss";
const statusMap = {
  0: { buttonText: "back", title: "plsWait", icon: Loading },
  1: { buttonText: "confirm", title: "almost", icon: Confirm },
  2: { buttonText: "continue", title: "allDone", icon: Success },
  3: { buttonText: "tryAgain", title: "ooops", icon: ErrorIcon },
};
const CallModal = ({
  status,
  children,
  content,
  open,
  buttonClickHandle,
  handleClose,
  buttonText,
  successCb,
}) => {
  const currentModelData = useMemo(() => {
    return statusMap[status];
  }, [status]);

  const Icon = useMemo(() => {
    return currentModelData.icon;
  }, [currentModelData]);

  return (
    <Model open={open} handleClose={handleClose}>
      <div className={cn(styles.confirmModel, styles["status" + status])}>
        <div className={styles.statusIcon}>
          <Icon />
        </div>
        <div className={styles.ModelContent}>
          <HeadLine>
            <Intl id={currentModelData.title} />
          </HeadLine>
          <div className={styles.content}>
            <Text type="large">{content}</Text>
          </div>
        </div>
        <div className={styles.extent}>{children}</div>
        <div className={styles.buttonGroup}>
          <Button
            onClick={() => {
              if (buttonClickHandle) {
                buttonClickHandle();
              } else {
                handleClose();
              }
            }}
          >
            <Text type="title">
              <Intl id={buttonText || currentModelData.buttonText} />
            </Text>
          </Button>
          {successCb && (
            <Button
              onClick={() => {
                successCb();
              }}
              className={styles.successCb}
            >
              <Text type="title">
                <Intl id="checkRequest" />
              </Text>
            </Button>
          )}
        </div>
      </div>
    </Model>
  );
};

export default CallModal;
