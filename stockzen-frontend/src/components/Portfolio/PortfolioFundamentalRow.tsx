import crossIcon from 'assets/icon-outlines/outline-cross.svg';
import React, { FC, useState } from 'react';
import { Link } from 'react-router-dom';
import { bigNumberFormatter, numberFormatter } from 'utils/Utilities';
import styles from './PortfolioPage.module.css';

interface PortfolioPageRowProp {
  readonly stock: IStockFundamental;
  readonly index: number;
  readonly showDeleteModal: (stockId: number, stock: string) => void;
}

const PortfolioFundamentalRow: FC<PortfolioPageRowProp> = (props) => {
  const { stock } = props;

  const [showPanel, setShowPanel] = useState(false);

  return (
    <div
      className={`${styles.stockWrapper} ${showPanel ? styles.panelVisible : styles.panelHidden
        }`}
    >
      <div className={styles.tableRow}>
        <div
          className={styles.rowStockInfo}
          onClick={() => {
            setShowPanel(!showPanel);
          }}
        >
          <span className={styles.rowHandle} />
          <span className={styles.infoRowCode}>
            <Link
              to={{
                pathname: `/stock/${stock.stockPageId}`,
                state: {
                  code: stock.code,
                  name: stock.name,
                }
              }}
              className={styles.rowStockLink}
            >
              {stock.code}
            </Link>
          </span>
          <div className={`${styles.infoRowName} d-none d-xxl-block`}>
            <div
              style={{ textOverflow: 'ellipsis', overflowX: 'hidden' }}
            >
              {stock.name}
            </div>
          </div>
          <span className={styles.rowInfo}>
            {stock.dayLow == null
              ? '-'
              : numberFormatter.format(stock.dayLow)}
          </span>
          <span className={styles.rowInfo}>
            {stock.dayHigh == null
              ? '-'
              : numberFormatter.format(stock.dayHigh)}
          </span>
          <span className={`${styles.rowLongInfo} d-none d-xxl-block`}>
            {stock.fiftyTwoWeekLow == null
              ? '-'
              : numberFormatter.format(stock.fiftyTwoWeekLow)}
          </span>
          <span className={`${styles.rowLongInfo} d-none d-xxl-block`}>
            {stock.fiftyTwoWeekHigh == null
              ? '-'
              : numberFormatter.format(stock.fiftyTwoWeekHigh)}
          </span>
          <span className={styles.rowLongInfo}>
            {stock.avgVolume == null
              ? '-'
              : bigNumberFormatter.format(stock.avgVolume)}
          </span>
          <span className={styles.rowLongInfo}>
            {stock.marketCap == null
              ? '-'
              : bigNumberFormatter.format(stock.marketCap)}
          </span>
          <span className={styles.rowShortInfo}>
            {stock.beta == null
              ? '-'
              : numberFormatter.format(stock.beta)}
          </span>
        </div>
      </div>
      <span className={styles.rowDelete}>
        <button
          className={`p-0 ${styles.deleteButton}`}
          onClick={() => {
            if (props.showDeleteModal != null) {
              props.showDeleteModal(stock.stockId, stock.name);
            }
          }}
        >
          <img src={crossIcon} alt='cross' />
        </button>
      </span>
    </div>
  );
};

export default PortfolioFundamentalRow;
